class DecisionEngine:

    def analyze(self, data: dict) -> dict:
        intent = data.get("intent", "unknown")
        urgency = data.get("urgency", "low")

        # -------------------------
        # Urgency Refinement Rules
        # -------------------------

        # Force high urgency for critical intents
        if intent == "emergency":
            urgency = "high"

        # Insurance claims → at least medium
        elif intent == "insurance claim" and urgency == "low":
            urgency = "medium"

        # Complaints → at least medium
        elif intent == "complaint" and urgency == "low":
            urgency = "medium"

        # Promotional → always low (override)
        elif intent == "promotional":
            urgency = "low"

        # Donations → usually low unless explicitly high
        elif intent == "donation" and urgency == "high":
            urgency = "medium"

        return {
            "intent": intent,
            "urgency": urgency,
            "entities": data.get("entities", {}),
            "original_text": data.get("original_text", "")
        }