from core.risk_manager import RiskManager

def test_enforce_caps():
    r = RiskManager("trial")
    size, allowed = r.enforce_caps(120, 50, 1)
    assert size == 25
    assert allowed
    _, allowed2 = r.enforce_caps(120, 10, 3)
    assert not allowed2

def test_daily_stop():
    r = RiskManager("pro", daily_loss_limit=-0.05)
    assert not r.check_daily_stop(1000, 950)
    assert r.check_daily_stop(1000, 940)

if __name__ == "__main__":
    test_enforce_caps()
    test_daily_stop()
    print("RiskManager tests passed")