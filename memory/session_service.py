
from datetime import datetime

class InMemorySessionService:
    def __init__(self):
        self.sessions = {}

    def get_session(self, user_id: str):
        if user_id not in self.sessions:
            self.sessions[user_id] = {"messages": [], "created": datetime.utcnow().isoformat()}
        return self.sessions[user_id]

    def add_message(self, user_id: str, role: str, text: str):
        session = self.get_session(user_id)
        session["messages"].append({"role": role, "text": text, "ts": datetime.utcnow().isoformat()})

    def append_user_entry(self, user_id: str, kind: str, entry: dict):
        session = self.get_session(user_id)
        session.setdefault(kind, []).append(entry)
