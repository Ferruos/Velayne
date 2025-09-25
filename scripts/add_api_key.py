import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from storage.db import get_session, APIKey
from services.crypto import encrypt

def main():
    user_id = int(input("Введите ваш user_id (Telegram): "))
    exchange = input("Биржа (например, binance): ").strip()
    api_key = input("API KEY: ").strip()
    api_secret = input("API SECRET: ").strip()
    session = get_session()
    db_key = APIKey(
        user_id=user_id,
        exchange=exchange,
        key_enc=encrypt(api_key),
        secret_enc=encrypt(api_secret)
    )
    session.add(db_key)
    session.commit()
    print("Ключи добавлены!")

if __name__ == "__main__":
    main()