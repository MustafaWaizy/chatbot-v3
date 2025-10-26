# logger.py
import json
from datetime import datetime
from pathlib import Path

UNKNOWN_LOG_FILE = Path("unmatched_inputs.json")

def log_unknown_input(user_input: str, suggestions: list):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "suggestions": suggestions
    }

    if UNKNOWN_LOG_FILE.exists():
        with open(UNKNOWN_LOG_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(log_entry)
            f.seek(0)
            json.dump(data, f, indent=2)
    else:
        with open(UNKNOWN_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([log_entry], f, indent=2)
