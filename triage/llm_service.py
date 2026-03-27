import json
import os
from dotenv import load_dotenv
from groq import Groq  

load_dotenv()
def __init__(self):
    self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class LLMService:

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def process_text(self, text: str) -> dict:
        prompt = self.get_prompt(text)

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",   # best model
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            output = response.choices[0].message.content.strip()
            parsed = self.safe_json_load(output)
            parsed["original_text"] = text   # ✅ ADD THIS LINE
            return parsed

        except Exception as e:
            print("LLM Error:", e)
            return self.fallback()

    # -------------------------
    # Prompt
    # -------------------------
    def get_prompt(self, text):
        return f"""
You are a strict JSON generator.

Your task is to analyze the email and return ONLY valid JSON.

Text:
\"\"\"{text}\"\"\"

Instructions:
- You MUST choose intent from:
  ["emergency", "return", "insurance claim", "promotional", "donation", "complaint"]

- You MUST choose urgency from:
  ["low", "medium", "high"]

- Extract entities carefully

- DO NOT return "unknown"
- DO NOT skip fields
- DO NOT add explanation
- Output MUST be valid JSON only



Output:
Example Output:
{{
  "intent": "return",
  "urgency": "low",
  "entities": {{
    "names": [],
    "dates": [],
    "phone_numbers": [],
    "emails": [],
    "ids": ["12345"],
    "locations": [],
    "amounts": []
  }}
}}

ONLY RETURN JSON.
"""

    # -------------------------
    # Safe JSON Parser
    # -------------------------

    def safe_json_load(self, text):
        import json
        import re
        try:
            return json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass


            return self.fallback()

    # -------------------------
    # Fallback
    # -------------------------
    def fallback(self):
        return {
            "intent": "unknown",
            "urgency": "low",
            "entities": {
                "names": [],
                "dates": [],
                "phone_numbers": [],
                "emails": [],
                "ids": [],
                "locations": [],
                "amounts": []
            },
            "original_text": ""   # ✅ ADD THIS
            
        }