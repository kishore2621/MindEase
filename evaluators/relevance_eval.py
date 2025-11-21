
import google.generativeai as genai

model = genai.GenerativeModel("gemini-2.0-flash")

def score_relevance(user_msg: str, reply: str) -> int:
    prompt = f"""
Score how relevant the assistant's reply is to the user message.
Scale: 1–10.
Return ONLY a number.

User: {user_msg}
Assistant: {reply}
"""
    res = model.generate_content(prompt)
    output = (res.text or "").strip()

    num = "".join(c for c in output if c.isdigit())
    if num:
        return int(num)

    return None

