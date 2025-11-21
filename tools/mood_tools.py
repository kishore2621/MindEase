
import json
from pathlib import Path
from datetime import date

def get_daily_summary(user_id: str, memory_path=None):
   
    if not memory_path:
        memory_path = Path(__file__).resolve().parents[1] / "memory" / "memory_bank.json"
    p = Path(memory_path)
    if not p.exists():
        return {"date": str(date.today()), "counts": {}, "total": 0}
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    counts = {}
    for e in data.get("entries", []):
        counts[e.get("emotion", "unknown")] = counts.get(e.get("emotion","unknown"), 0) + 1
    total = sum(counts.values())
    return {"date": str(date.today()), "counts": counts, "total": total}
