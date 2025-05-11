import pandas as pd
from .base_matcher import MatchStrategy


class ModeAStrategy(MatchStrategy):
    def match(self) -> pd.DataFrame:
        df = self.trades.copy()
        merged = df.merge(
            df,
            on="symbol",
            suffixes=("_a", "_b")
        )
        # Drop self-joins
        merged = merged[merged["identifier_a"] < merged["identifier_b"]]
        return self._prepare_matches(merged)