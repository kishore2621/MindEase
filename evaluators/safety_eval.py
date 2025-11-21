
import google.generativeai as genai

MODEL = "gemini-1.5-flash"

def check_safety(text: str) -> str:
    model = genai.GenerativeModel(MODEL)
    prompt = f"""
Check the following user message for safety. Return one of: safe, mild-risk, self-harm-risk.
Message: "{text}"

Return only the label.
"""
    try:
        r = model.generate_content(prompt).text.strip().lower()
        return r
    except Exception:
        return "safe"
