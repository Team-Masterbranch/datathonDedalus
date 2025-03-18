import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Use absolute path for chat history
CHAT_HISTORY_DIR = Path(__file__).parent.parent / 'chat_history'
CHAT_HISTORY_DIR.mkdir(exist_ok=True, parents=True)

def get_chat_session(session_id: str) -> Optional[Dict]:
    """Get full chat session by ID"""
    try:
        file_path = CHAT_HISTORY_DIR / f"{session_id}.json"
        if not file_path.exists():
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading session {session_id}: {str(e)}")
        return None

def save_chat_session(session_id: str, messages: List[Dict], metadata: Dict = None) -> Path:
    """Save a chat session to JSON file"""
    try:
        file_path = CHAT_HISTORY_DIR / f"{session_id}.json"
        data = {
            "meta": metadata or {},
            "messages": messages,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved chat session to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving chat session: {str(e)}")
        raise

def load_chat_history() -> List[Dict]:
    """Load all available chat histories"""
    sessions = []
    try:
        for file_path in CHAT_HISTORY_DIR.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    sessions.append({
                        "id": file_path.stem,
                        "timestamp": data.get("timestamp"),
                        "preview": data["messages"][0]["text"] if data["messages"] else "Empty chat",
                        "path": str(file_path)
                    })
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
        return sorted(sessions, key=lambda x: x["timestamp"], reverse=True)
    except Exception as e:
        logger.error(f"Error loading chat history: {str(e)}")
        return []