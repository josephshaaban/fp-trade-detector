import pandas as pd
from trades.risk_engine.matcher.base_matcher import MatchStrategy


class ModeAStrategy(MatchStrategy):
    def __init__(self, trades: pd.DataFrame, accounts: pd.DataFrame):
        super().__init__(trades, accounts)
        self.name = "Mode A"
        self.mode = "A"

    def _match(self) -> None:
        df = self.matched.copy()
        merged = df.merge(
            df,
            on="symbol",
            suffixes=("_a", "_b")
        )
        # Drop self-joins
        merged = merged[merged["identifier_a"] < merged["identifier_b"]]

        self.matched = merged.copy()