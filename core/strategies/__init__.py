from .ema import EMAStrategy
from .mean_reversion import MeanReversionStrategy
from .breakout import BreakoutStrategy

STRATEGY_CLASSES = [
    EMAStrategy,
    MeanReversionStrategy,
    BreakoutStrategy,
]