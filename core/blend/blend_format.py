"""
Схема JSON для blend:
{
  "version": "2024092501",
  "components": [
    {"name": "EMA", "params": {...}, "weight": 0.3},
    {"name": "MeanReversion", "params": {...}, "weight": 0.4},
    {"name": "Breakout", "params": {...}, "weight": 0.3}
  ],
  "metrics": {"score": 0.9, ...},
  "regime": "trend"
}
"""
def validate_blend(blend_json):
    assert "version" in blend_json
    assert "components" in blend_json
    assert isinstance(blend_json["components"], list)
    assert all("name" in c and "params" in c and "weight" in c for c in blend_json["components"])
    assert "regime" in blend_json
    return True