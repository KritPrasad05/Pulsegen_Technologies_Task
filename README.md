
# 🧬 Pulsegen: AI Module Extractor

🎥 **Demo Video:**  

A complete screen recording demonstrating the working of this project is available here:  
👉 **[[Google Drive Demo Link – replace with your actual link](https://drive.google.com/file/d/1Q7dKgwIHtR4yrC9gXMHJ42AN6yV7ykzu/view?usp=sharing )]**

---

## 📌 Overview

**Pulsegen** is an AI-powered intelligent agent that autonomously crawls documentation websites, analyzes their structure, and extracts product **Modules** and **Submodules** into a clean, structured JSON format.

The system is designed to simulate how a **Senior AI Engineer** would build a documentation intelligence pipeline: robust crawling, content normalization, LLM-driven semantic reasoning, and user-facing visualization.

---

## 🚀 Key Features

- **Multi-Source Extraction**  
  Process multiple documentation URLs simultaneously (comma-separated).

- **Recursive Crawling (BFS)**  
  Automatically discovers and crawls internal documentation links.

- **Intelligent Content Normalization**  
  - Converts HTML tables into Markdown-like text  
  - Preserves lists and hierarchical structure for better LLM understanding

- **AI-Powered Semantic Extraction**  
  Uses **Google Gemini** to infer modules and submodules even from sparse landing pages or navigation-heavy docs.

- **Real-Time Visual Feedback**  
  Live crawl progress, statistics, and error reporting via Streamlit UI.

- **Structured Output**  
  Downloadable, well-structured JSON reports — segregated per documentation source.

---

## 🛠️ Technical Architecture

### Tech Stack

- **Frontend / UI:** Streamlit (Python)
- **Crawler:** `requests` + `BeautifulSoup4`
- **LLM Engine:** Google Gemini (tested with `gemini-2.5-flash`)
- **Data Format:** JSON
- **Environment Management:** `python-dotenv`

---

## 📁 Project Structure

```text
PLT_TASK/
├── app/
│   └── core/
│       └── llm_gemini.py        # Gemini LLM wrapper
├── crawler.py                   # RobustCrawler logic (validation + normalization)
├── main.py                      # Streamlit UI & orchestration
├── check_models.py              # Utility to verify Gemini model access
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
└── README.md                    # Project documentation
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python **3.10+**
- A **Google Gemini API key**  
  👉 Get one from: https://aistudio.google.com/

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/pulsegen-extractor.git
cd pulsegen-extractor
```

---

### Step 2: Install Dependencies

It is recommended to use a virtual environment.

```bash
pip install -r requirements.txt
```

---

### Step 3: Configure Environment Variables

1. Rename `.env.example` → `.env`
2. Open `.env` and add your API key:

```env
GEMINI_API_KEY=AIzaSy...your_actual_key...
```

---

### Step 4: Run the Application

```bash
streamlit run main.py
```

The application will open in your browser at:  
👉 http://localhost:8501

---

## 📖 Usage Guide

1. **Launch the App**  
   Open the Streamlit UI in your browser.

2. **Enter Documentation URLs**  
   Provide one or more URLs separated by commas.

   **Example:**
   ```
   https://wordpress.org/documentation/, https://docs.python.org/3/
   ```

3. **Processing Pipeline**
   - 🕷️ Crawl documentation pages
   - 🧠 Analyze content using Gemini
   - ✅ Generate structured module/submodule JSON

4. **Download Output**
   Click **“Download Consolidated JSON”** to save the results.

---

## 🔍 Compatibility & Limitations

### ✅ Supported (Static / SSR Websites)

Works best on documentation sites where content is present in the raw HTML:

- WordPress Docs — https://wordpress.org/documentation/
- Python Docs — https://docs.python.org/3/
- Chargebee Docs — https://www.chargebee.com/docs/2.0/
- Zluri Help — https://help.zluri.com/

---

### ❌ Limited Support (Dynamic / SPA Websites)

Sites that rely heavily on JavaScript rendering may return partial data:

- Instagram Help (JS-heavy, requires Selenium/Playwright)
- Neo.Space (bot-protected)

📌 *In such cases, the AI attempts to infer modules from page titles and menus where possible.*

---

## 🧩 Key Implementation Highlights

### 1️⃣ Robust Content Normalization

HTML tables are converted into Markdown-style text for better LLM comprehension:

```python
def normalize_content(self, soup):
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            rows.append(" | ".join(cells))
        table_text = "\n" + "\n".join(rows) + "\n"
        table.replace_with(table_text)
    return soup.get_text(separator=' ', strip=True)
```

---

### 2️⃣ Strict JSON-Only AI Extraction

The prompt enforces deterministic, machine-readable output:

```python
prompt = f"""
You are a Technical Architect. Extract product modules from this documentation.

STRICT OUTPUT RULES:
1. Return ONLY valid JSON.
2. Structure:
   [
     {{
       "module": "Name",
       "Description": "...",
       "Submodules": {{
         "Name": "Description"
       }}
     }}
   ]
3. If content is a landing/menu page, infer modules from titles.

CONTENT:
{raw_text[:80000]}
"""
```

---

## 📝 Assumptions

- **Documentation Structure:** Hierarchical (topics → subtopics)
- **Language:** English
- **Content Priority:** URLs containing `/doc`, `/guide`, or `/help`

---

## 🤝 Troubleshooting

### Model Access Issues

If you encounter a *“model not found”* error, verify which Gemini models are available to your API key:

```bash
python check_models.py
```

---

## 📜 License

This project is open-source and free to use for educational and demonstration purposes.

---

**Pulsegen AI — Documentation Intelligence Agent**
