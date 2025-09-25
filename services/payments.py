from storage.db import Payment, get_session
from sqlmodel import select
from datetime import datetime

def create_payment(user_id, amount, currency="RUB"):
    with get_session() as session:
        payment = Payment(user_id=user_id, amount=amount, currency=currency)
        session.add(payment)
        session.commit()
        return payment.id

def check_yoomoney_payment(payment_id):
    print("Юкасса токен не задан. Проверка оплаты невозможна.")
    return False

def is_user_paid(user_id):
    with get_session() as session:
        q = select(Payment).where(Payment.user_id == user_id, Payment.status == "confirmed")
        payment = session.exec(q).first()
        return payment is not None