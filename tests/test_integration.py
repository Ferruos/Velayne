"""
Интеграционные тесты: run/stop, подписка, blend, ключи.
"""
from storage.db import init_db, get_session, User
from services.crypto import encrypt, decrypt
from services.payments import process_payment
from master.master import publish_blend
from workers.worker import run_worker

def test_crypto():
    secret = "supersecret"
    enc = encrypt(secret)
    dec = decrypt(enc)
    assert secret == dec

def test_subscription():
    session = get_session()
    u = User(tg_id=12345)
    session.add(u)
    session.commit()
    _, sub = process_payment(u.id, "basic")
    assert sub.plan == "basic"

def test_blend_publish_and_worker():
    import numpy as np
    prices = np.cumsum(np.random.randn(200)) + 100
    publish_blend(prices)
    run_worker(1, "sandbox")  # user_id=1

if __name__ == "__main__":
    init_db()
    test_crypto()
    test_subscription()
    test_blend_publish_and_worker()
    print("Integration tests passed")