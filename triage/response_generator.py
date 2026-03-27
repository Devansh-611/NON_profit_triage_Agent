import json
import os
from dotenv import load_dotenv
from groq import Groq  

load_dotenv()
def __init__(self):
    self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class ResponseGenerator:

    def __init__(self):
        self.client = Groq()

    def generate(self, decision: dict) -> str:
        prompt = self.build_prompt(decision)

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        return response.choices[0].message.content.strip()

    # -------------------------
    # Prompt Builder
    # -------------------------
    def build_prompt(self, decision):
       return f"""
You are a professional customer support agent for a non-profit organization.

Your role is to:
- Acknowledge the request
- Show empathy if requried
- Inform the user that the request is being reviewed
- NEVER directly approve or reject requests (like refund, claim, etc.)
Original Email:
\"\"\"{decision.get("original_text", "")}\"\"\"

Extracted Analysis:
{json.dumps(decision, indent=2)}

Instructions:
- DO NOT confirm actions like "refund approved", "claim processed", etc.
- Understand the full context from the original email
- Use extracted entities naturally (name, ID, date, etc.)
- Maintain a professional and empathetic tone
- Adapt tone based on urgency:
  - high → urgent + reassuring
  - medium → attentive 
  - low → calm and helpful
- DO NOT mention "intent" or "urgency"
- Make response specific (NOT generic)
- Keep it concise but meaningful

Output:
Generate ONLY the final email response.
"""