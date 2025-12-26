import streamlit as st
import json
import time
from app.core.llm_gemini import GeminiLLM
from crawler import RobustCrawler

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Pulsegen AI Agent",
    page_icon="🤖",
    layout="wide"
)

# --- CUSTOM CSS (THE FIX) ---
st.markdown("""
<style>
    /* 1. Center the Chat Input and make it floating */
    .stChatInput {
        position: fixed;
        bottom: 40px; /* Move it up slightly */
        left: 50%;
        transform: translateX(-50%); /* Perfect horizontal centering */
        width: 100%;
        max-width: 800px; /* Restrict width to look like a chat box */
        z-index: 1000;
    }

    /* 2. Add padding to main container so content isn't hidden behind the input */
    .block-container {
        padding-bottom: 150px;
    }
    
    /* 3. Style the Header */
    h1 {
        text-align: center;
        color: #4F46E5;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("Pulsegen Module Extractor")
st.markdown(
    "<p style='text-align: center; color: gray;'>Enter documentation URLs (comma-separated) below. <br>I will process them one by one and segregate the results.</p>", 
    unsafe_allow_html=True
)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [] 
if "full_results" not in st.session_state:
    st.session_state.full_results = {} 

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("is_json"):
            st.json(message["content"], expanded=False)
        else:
            st.markdown(message["content"])

# --- MAIN LOGIC ---
if prompt := st.chat_input("Ex: https://www.chargebee.com/docs/2.0/, https://help.zluri.com/"):
    
    # 1. Show User Input
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Parse URLs
    urls = [u.strip() for u in prompt.split(',') if u.strip()]
    
    if not urls:
        st.error("Please enter valid URLs.")
    else:
        run_results = {}
        
        with st.chat_message("assistant"):
            st.markdown(f"**Starting extraction for {len(urls)} sources...**")
            
            # Global Progress Bar
            main_progress = st.progress(0)
            step_size = 1.0 / len(urls)

            # --- LOOP THROUGH EACH URL ---
            for i, target_url in enumerate(urls):
                
                # Visual Divider
                st.divider()
                st.markdown(f"### 📂 Source: `{target_url}`")
                status_box = st.empty()
                
                try:
                    # A. CRAWL
                    status_box.info(f"Crawling {target_url}...")
                    crawler = RobustCrawler()
                    raw_text, visited, errors = crawler.crawl([target_url], max_pages_per_domain=6)
                    
                    if not raw_text:
                        st.error(f"⚠️ Could not extract content from {target_url}.")
                        continue

                    # B. AI PROCESSING
                    status_box.info(f"Identifying modules for {target_url}...")
                    
                    ai_prompt = f"""
                    You are a Technical Architect. Extract product modules from this documentation.
                    
                    STRICT OUTPUT RULES:
                    1. Return ONLY valid JSON.
                    2. Structure: [ {{"module": "Name", "Description": "...", "Submodules": {{ "Name": "Desc" }} }} ]
                    3. If text is a menu/landing page, infer modules from the titles.
                    
                    CONTENT SOURCE: {target_url}
                    CONTENT:
                    {raw_text[:80000]} 
                    """
                    
                    llm = GeminiLLM()
                    response = llm.generate(ai_prompt)
                    
                    # Clean JSON
                    json_str = response.replace("```json", "").replace("```", "").strip()
                    data = json.loads(json_str)
                    
                    # C. DISPLAY RESULT
                    status_box.success(f"✅ Extracted {len(data)} modules.")
                    st.json(data, expanded=False)
                    
                    run_results[target_url] = data
                    
                    # Debug Info
                    with st.expander(f"Crawl Stats for {target_url}"):
                        st.write(f"Pages Scanned: {len(visited)}")
                        st.code(visited)

                except Exception as e:
                    st.error(f"❌ Error processing {target_url}: {str(e)}")
                
                # Update Progress
                main_progress.progress(min((i + 1) * step_size, 1.0))

            # --- FINALIZE ---
            main_progress.empty()
            
            if run_results:
                st.session_state.full_results.update(run_results)
                
                st.success("All sources processed successfully!")
                
                # Master JSON Download
                master_json = json.dumps(run_results, indent=2)
                st.download_button(
                    label="📥 Download Consolidated JSON",
                    data=master_json,
                    file_name="modules_consolidated.json",
                    mime="application/json"
                )
                
                # Save Summary to History
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Processed {len(run_results)} URLs. Check results above."
                })