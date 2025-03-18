import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

CHAT_HISTORY_DIR = Path("chat_history")
CHAT_HISTORY_DIR.mkdir(exist_ok=True)

def save_chat_session(session_id: str, messages: List[Dict], metadata: Dict = None) -> Path:
    """Save a chat session to JSON file"""
    file_path = CHAT_HISTORY_DIR / f"{session_id}.json"
    data = {
        "meta": metadata or {},
        "messages": messages,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return file_path

def load_chat_history() -> List[Dict]:
    """Load all available chat histories"""
    sessions = []
    for file_path in CHAT_HISTORY_DIR.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                sessions.append({
                    "id": file_path.stem,
                    "timestamp": data.get("timestamp"),
                    "preview": data["messages"][0]["text"] if data["messages"] else "Empty chat",
                    "path": file_path
                })
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
    
    return sorted(sessions, key=lambda x: x["timestamp"], reverse=True)

def get_chat_session(session_id: str) -> Optional[Dict]:
    """Get full chat session by ID"""
    file_path = CHAT_HISTORY_DIR / f"{session_id}.json"
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)