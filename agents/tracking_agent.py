
import json
from pathlib import Path

class TrackingAgent:
    def __init__(self, mood_log_path):
        self.log_path = Path(mood_log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump({"entries": []}, f)

    def log_mood(self, emotion: str, note: str):
        entry = {"emotion": emotion, "note": note}
        with open(self.log_path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("entries", []).append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
