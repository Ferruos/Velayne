from storage.db import APIKey, get_session
from sqlmodel import select
import ccxt

def encrypt(s):
    # Для простоты — реальное шифрование подставь своё!
    return s[::-1]

def decrypt(s):
    return s[::-1]

def add_api_key(user_id, exchange, api_key, api_secret):
    key_enc = encrypt(api_key)
    secret_enc = encrypt(api_secret)
    is_valid = validate_api_key(exchange, api_key, api_secret)
    with get_session() as session:
        db_key = APIKey(
            user_id=user_id,
            exchange=exchange,
            key_enc=key_enc,
            secret_enc=secret_enc,
            is_valid=is_valid
        )
        session.add(db_key)
        session.commit()
        return is_valid

def validate_api_key(exchange, api_key, api_secret):
    try:
        ex = getattr(ccxt, exchange)({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True
        })
        ex.fetch_balance()
        return True
    except Exception:
        return False

def get_keys_info(user_id):
    with get_session() as session:
        keys = session.exec(select(APIKey).where(APIKey.user_id == user_id)).all()
        res = []
        for k in keys:
            status = "✅" if k.is_valid else "❌"
            res.append(f"{k.exchange}: {status}")
        return "\n".join(res) if res else "Нет ключей."