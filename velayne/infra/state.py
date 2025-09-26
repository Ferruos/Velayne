import json
from pathlib import Path
from datetime import datetime
from velayne.infra.config import settings

STATE_FILE = Path(settings.DATA_DIR) / "state.json"

DEFAULT_STATE = {
    "mode": "sandbox",
    "users": {}
}

def _ensure_dirs():
    Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.DATA_DIR).mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_STATE, f, ensure_ascii=False, indent=2)

def _read_state():
    _ensure_dirs()
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _write_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_mode() -> str:
    state = _read_state()
    return state.get("mode", "sandbox")

def set_mode(new_mode: str):
    state = _read_state()
    state["mode"] = new_mode
    _write_state(state)

def ensure_user(tg_id: int):
    state = _read_state()
    tg_id_str = str(tg_id)
    if tg_id_str not in state["users"]:
        state["users"][tg_id_str] = {
            "consent": False,
            "created_at": datetime.utcnow().isoformat()
        }
        _write_state(state)

def set_consent(tg_id: int, consent: bool):
    state = _read_state()
    tg_id_str = str(tg_id)
    if tg_id_str in state["users"]:
        state["users"][tg_id_str]["consent"] = bool(consent)
        _write_state(state)

def list_users():
    state = _read_state()
    return [
        {"id": int(uid), **udata}
        for uid, udata in state.get("users", {}).items()
    ]