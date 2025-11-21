
import json
from datetime import datetime

def log_event(name, payload):
    
    print(f"[{datetime.utcnow().isoformat()}] {name} - {json.dumps(payload, default=str)}")
