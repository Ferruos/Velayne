import json
import datetime
import threading
from typing import Dict, Any, Optional
from services.logging import get_logger

logger = get_logger("blend")
BLEND_FILE = "blend.json"
_lock = threading.Lock()  # Для потокобезопасности

class BlendManager:
    def __init__(self, _unused_url: Optional[str] = None):
        pass

    def publish_blend(self, blend: Dict[str, Any]):
        blend["created_at"] = datetime.datetime.utcnow().isoformat()
        with _lock:
            with open(BLEND_FILE, "w", encoding="utf-8") as f:
                json.dump(blend, f, ensure_ascii=False, indent=2)
        logger.info(f"Blend saved to {BLEND_FILE}")

    def get_current_blend(self) -> Optional[Dict[str, Any]]:
        try:
            with _lock:
                with open(BLEND_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except FileNotFoundError:
            logger.warning(f"{BLEND_FILE} not found, returning None")
            return None
        except Exception as e:
            logger.error(f"Error reading {BLEND_FILE}: {e}")
            return None