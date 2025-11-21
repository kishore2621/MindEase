
import google.generativeai as genai

class ExerciseAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def suggest(self, emotion: str) -> str:
       
        if emotion in ["happy", "neutral"]:
            return None

        
        prompt = f"""
Provide a short (10–25 second) exercise for someone feeling **{emotion}**.
It must be different each time. You can include variations like:
- grounding
- breathing
- muscle relaxation
- visualization

Return ONLY the exercise text. No formatting, no titles.
"""

        result = self.model.generate_content(prompt)
        return result.text.strip()