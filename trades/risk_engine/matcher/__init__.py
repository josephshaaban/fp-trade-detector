import pandas as pd

from .base_matcher import MatchStrategy
from .mode_a_matcher import ModeAStrategy
from .mode_b_matcher import ModeBStrategy


def get_strategy(mode: str, trades: pd.DataFrame, accounts: pd.DataFrame) -> MatchStrategy:
    strategies = {
        "A": ModeAStrategy,
        "B": ModeBStrategy,
    }
    if mode not in strategies:
        raise ValueError(f"Unsupported mode: {mode}")
    return strategies[mode](trades, accounts)


__all__ = ["get_strategy", "MatchStrategy", "ModeAStrategy", "ModeBStrategy"]
