
import google.generativeai as genai

model = genai.GenerativeModel("gemini-2.0-flash")

def score_empathy(text: str) -> int:
    prompt = f"""
Rate how empathetic the following response is on a scale of 1-10.
Return ONLY a number.

Response:
\"\"\"{text}\"\"\"
"""
    res = model.generate_content(prompt)
    output = (res.text or "").strip()

   
    num = "".join(c for c in output if c.isdigit())
    if num:
        return int(num)

    return None

