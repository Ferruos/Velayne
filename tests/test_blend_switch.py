"""
Интеграционный тест: смена blend и дренаж позиций.
"""
from core.blend.meta_policy import MetaPolicy

def test_blend_switch_and_drain():
    blends_by_mode = {
        "trend": {"version": "1", "components": [{"name": "EMA", "params": {}, "weight": 1}]},
        "range": {"version": "2", "components": [{"name": "MeanReversion", "params": {}, "weight": 1}]},
        "default": {"version": "1", "components": [{"name": "EMA", "params": {}, "weight": 1}]}
    }
    meta = MetaPolicy(blends_by_mode)
    assert meta.select_blend("trend")["version"] == "1"
    assert meta.select_blend("range")["version"] == "2"
    assert meta.select_blend("panic")["version"] == "1"  # default