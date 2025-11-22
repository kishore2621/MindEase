import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0]))

from datetime import datetime, timezone

from flask import Flask, request, jsonify
from flask_cors import CORS

import google.generativeai as genai
from dotenv import load_dotenv



# Load environment variables (Vercel also injects env vars automatically)
load_dotenv()

# Retrieve env vars
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found. Add it in Vercel → Settings → Environment Variables")

genai.configure(api_key=GEMINI_API_KEY)

# Correct static folder path for Vercel
PUBLIC_FOLDER = str(Path(__file__).resolve().parents[1] / "public")

app = Flask(__name__, static_folder=PUBLIC_FOLDER, static_url_path="/")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Import internal modules after app is created
from memory.session_service import InMemorySessionService
from utils.logger import log_event
from utils.context_compactor import compact_context
from agents.emotion_agent import EmotionAgent
from agents.coach_agent import CoachAgent
from agents.exercise_agent import ExerciseAgent
from agents.tracking_agent import TrackingAgent
from evaluators.empathy_eval import score_empathy
from evaluators.safety_eval import check_safety
from evaluators.relevance_eval import score_relevance
from tools.mood_tools import get_daily_summary

# Initialize agents and services
session_svc = InMemorySessionService()
emotion_agent = EmotionAgent()
coach_agent = CoachAgent()
exercise_agent = ExerciseAgent()

tracking_agent = TrackingAgent(
    mood_log_path=str(Path(__file__).resolve().parents[1] / "memory" / "memory_bank.json")
)

# --------------- FRONTEND ROUTE --------------------
@app.route("/")
def homepage():
    return app.send_static_file("index.html")

# --------------- CHAT API --------------------------
@app.route('/api/chat', methods=['POST'])
def chat():
    payload = request.get_json(force=True)
    user_id = payload.get("user_id", "anon")
    text = (payload.get("text") or "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Retrieve session
    session = session_svc.get_session(user_id)
    session_svc.add_message(user_id, "user", text)

    # Context compression
    try:
        messages_for_compaction = [
            {"role": m["role"], "content": m["text"]} 
            for m in session.get("messages", [])
        ]
        summary = compact_context(messages_for_compaction)
        if summary:
            session["messages"] = [
                {"role": "system", "text": f"COMPRESSED_SUMMARY: {summary}"}
            ] + session["messages"][-8:]
    except:
        pass

    # Emotion agent
    try:
        emotion = emotion_agent.analyze(text)
    except Exception as e:
        print("==== Errorrr ====")
        print(f"Error message: {e}")
        emotion = "neutral"

    # Safety
    try:
        safety_label = check_safety(text)
    except:
        
        safety_label = "safe"

    if "unsafe" in safety_label or "self-harm" in safety_label:
        return jsonify({
            "type": "crisis",
            "message": "It sounds like you're in danger. Please contact emergency services."
        })

    # Coach reply
    try:
        coach_reply = coach_agent.reply(text, emotion)
    except:
        coach_reply = "I'm here with you. Tell me more."

    # Exercise suggestion
    try:
        exercise_text = exercise_agent.suggest(emotion)
    except:
        exercise_text = "Try deep breathing."

    # Save messages
    session_svc.add_message(user_id, "agent", coach_reply)
    session_svc.add_message(user_id, "agent", exercise_text)

    return jsonify({
        "type": "reply",
        "emotion": emotion,
        "coach": {"reply": coach_reply},
        "exercise": {"exercise": exercise_text},
        "evaluation": {
            "safety_label": safety_label
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

# --------------- SUMMARY TITLE ---------------------
@app.route('/api/summarize', methods=['POST'])
def summarize_title():
    """
    Generate a short, descriptive chat title from a user's first message.
    Request body: { "text": "<user message>" }
    Response: { "title": "<short title>" }
    """
    try:
        payload = request.get_json(force=True) or {}
        text = (payload.get('text') or "").strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Prompt: ask LLM for a short (<=6 words) title
        prompt = f"""
You are a helpful assistant that writes a concise chat title (max 6 words) that summarizes the user's message.
Do not include punctuation or quotes. Keep it short and specific.

User message:
\"\"\"{text}\"\"\"

Return a single short title.
"""
        try:
            model = genai.GenerativeModel(MODEL)
            res = model.generate_content(prompt)
            title = (res.text or "").strip()
            # Basic cleanup: keep only first line, trim punctuation
            title = title.splitlines()[0].strip()
            # limit words to 6
            title_words = title.split()
            if len(title_words) > 6:
                title = " ".join(title_words[:6])
            # fallback if empty
            if not title:
                raise ValueError("empty title")
            return jsonify({"title": title}), 200
        except Exception as e:
            # log and fallback
            log_event('summarize.error', {'error': str(e)})
            # fallback title: first 5 words of the text
            fallback = " ".join(text.split()[:5]) + ("..." if len(text.split())>5 else "")
            return jsonify({"title": fallback}), 200

    except Exception as e:
        log_event('summarize.unexpected', {'error': str(e)})
        return jsonify({"error": "internal error"}), 500


    prompts = [
        "What’s one small thing you’re grateful for today?",
        "Describe one moment today when you felt even slightly better.",
        "What’s one small goal for tomorrow?"
    ]
    return jsonify({'prompt': prompts[0]}), 200
    payload = request.json or {}
    text = payload.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    prompt = f"Create a 6-word title: {text}"

    try:
        model = genai.GenerativeModel(MODEL)
        res = model.generate_content(prompt)
        title = res.text.strip().splitlines()[0]
    except:
        title = " ".join(text.split()[:6])

    return jsonify({"title": title})

# --------------- JOURNAL APIs ---------------------
@app.route('/api/journal_prompt', methods=['GET'])
def journal_prompt():
    payload = request.json or {}
    user_id = payload.get("user_id", "anon")
    entry = payload.get("entry", "")

    session_svc.append_user_entry(user_id, "journal", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entry": entry
    })

    return jsonify({"ok": True})

@app.route('/api/daily_summary', methods=['GET'])
def daily_summary():
    user_id = request.args.get("user_id", "anon")
    return jsonify(get_daily_summary(user_id))

# ----------- Disable caching -----------------------
@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response

# DO NOT ADD `app.run()` HERE → Vercel runs this file automatically
