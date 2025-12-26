import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiLLM:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=self.api_key)
        
        # FIXED: gemini-1.5-flash is deprecated. Switched to 2.5-flash.
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback: If 2.5 fails, try the generic alias 'gemini-pro'
            try:
                fallback_model = genai.GenerativeModel('gemini-pro')
                response = fallback_model.generate_content(prompt)
                return response.text
            except Exception as fallback_error:
                return f"Error generating content: {str(e)} | Fallback error: {str(fallback_error)}"