
import google.generativeai as genai
MODEL = "gemini-1.5-flash"

def compact_context(conversation: list) -> str:
    """
    conversation: list of {role, content}
    Return short summary string or None
    """
    if not conversation or len(conversation) < 8:
        return None

    text = "\n".join([f"{m['role']}: {m['content']}" for m in conversation[-50:]])
    prompt = f"""
Summarize the following chat history into a concise memory (max 3 sentences).
Preserve emotional state, user goals, and ongoing context.

{text}
"""
    try:
        model = genai.GenerativeModel(MODEL)
        r = model.generate_content(prompt).text.strip()
        return r
    except Exception:
        return None
