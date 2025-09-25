from storage.repositories import UserRepo, SubscriptionRepo
from services.subscription import renew_subscription, get_plan
from core.blend.blend_manager import BlendManager
from core.portfolio import PortfolioManager
from workers.worker import get_market_data

def test_full_cycle():
    user = UserRepo.create(42)
    renew_subscription(user, SubscriptionRepo, "Trial")
    bm = BlendManager("redis://localhost:6379/0")
    plan = get_plan("Trial")
    pm = PortfolioManager(bm, plan)
    # Mock blend
    bm.publish_blend({
        "version": "test",
        "components": [{"name": "EMA", "params": {"fast": 5, "slow": 20}, "weight": 1}],
        "metrics": {},
        "regime": "trend"
    })
    market_data = get_market_data()
    order = pm.aggregate_signals(user["id"], market_data)
    assert order["action"] in ("buy", "sell", "hold")