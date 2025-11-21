
import google.generativeai as genai

MODEL = "gemini-1.5-flash"

class CoachAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def reply(self, text: str, emotion: str) -> str:
        
        lower = text.strip().lower()
        greetings = ("hi","hello","hey","good morning","good evening","good afternoon")
        if any(lower.startswith(g) for g in greetings) and len(lower.split()) <= 3:
            return "Hi there! I'm MindEase — how are you feeling today?"

        prompt = f"""
You are a warm, empathetic mental wellness coach.
User emotion: {emotion}
User message: "{text}"

Write a short empathetic response (2-4 sentences). Do not give medical advice.
"""
        result = self.model.generate_content(prompt)
        return result.text.strip()
