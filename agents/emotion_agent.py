
import google.generativeai as genai

MODEL = "gemini-2.0-flash"

class EmotionAgent:
    def __init__(self):
        self.model = genai.GenerativeModel(MODEL)

    def normalize_emotion(self, raw: str) -> str:
        raw = raw.lower().strip()

        
        for prefix in ["emotion:", "the user feels", "the user is", "feeling", "feels"]:
            if raw.startswith(prefix):
                raw = raw.replace(prefix, "").strip()

        
        synonyms = {
            "angry": ["angry", "anger", "mad", "irritated", "annoyed", "rage"],
            "sad": ["sad", "down", "unhappy", "depressed", "low"],
            "stressed": ["stressed", "stress", "tense"],
            "anxious": ["anxious", "anxiety", "nervous", "worried"],
            "overwhelmed": ["overwhelmed", "overwhelm"],
            "frustrated": ["frustrated", "frustrating"],
            "happy": ["happy", "joy", "joyful", "good", "positive"],
            "neutral": ["neutral", "okay", "fine", "alright"]
        }

        
        for emotion, words in synonyms.items():
            if raw in words:
                return emotion
            if any(word in raw for word in words):
                return emotion

        return "neutral"

    def analyze(self, text: str) -> str:
        prompt = f"""
Classify the user’s primary emotion using ONE word only.

Valid emotions:
stressed, anxious, overwhelmed, sad, angry, frustrated, happy, neutral.

User message: "{text}"

Return ONLY the emotion word. No sentences. No punctuation.
"""
        result = self.model.generate_content(prompt)
        raw_emotion = result.text.strip().lower()
        return self.normalize_emotion(raw_emotion)
