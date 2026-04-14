class DecisionEngine:

    def analyze(self, data: dict) -> dict:
        intent = data.get("intent", "unknown")
        urgency = data.get("urgency", "low")


        # Urgency Refinement Rules
   

        # Force high urgency for critical intents
        if intent == "emergency":
            urgency = "high"


 

        # Promotional → always low (override)
        elif intent == "promotional":
            urgency = "low"



        return {
            "intent": intent,
            "urgency": urgency,
            "entities": data.get("entities", {}),
            "original_text": data.get("original_text", "")
        }