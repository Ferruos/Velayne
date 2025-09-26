def test_strategies_regression_pass():
    from velayne.core.strategies_regression import run_regression
    result = run_regression()
    assert result["all_pass"], f"Regression failed: {result['results']}"