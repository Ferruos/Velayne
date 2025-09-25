from core.risk import enforce_plan_caps

class Plan:
    max_order_size = 100

def test_enforce_plan_caps():
    order = {"action": "buy", "amount": 200}
    plan = Plan()
    capped = enforce_plan_caps(order, plan)
    assert capped['amount'] == 100

def test_enforce_no_caps():
    order = {"action": "buy", "amount": 50}
    plan = Plan()
    capped = enforce_plan_caps(order, plan)
    assert capped['amount'] == 50