import pandas as pd
from .base_matcher import MatchStrategy


class ModeBStrategy(MatchStrategy):
    def __init__(self, trades: pd.DataFrame, accounts: pd.DataFrame):
        super().__init__(trades, accounts)
        self.name = "Mode B"
        self.mode = "B"
        self.add_postprocessor(self.add_violation_flag)

    @staticmethod
    def add_violation_flag(df: pd.DataFrame) -> pd.DataFrame:
        df["is_violation"] = df["category"].isin(["copy", "reverse", "partial"])
        return df
    
    def match(self) -> pd.DataFrame:
        df = self.trades.copy()
        merged = df.merge(
            df,
            on="symbol",
            suffixes=("_a", "_b")
        )
        merged = merged[merged["identifier_a"] < merged["identifier_b"]]

        # Inject user_ids for filtering
        merged["user_id_a"] = merged["trading_account_login_a"].map(self.account_to_user)
        merged["user_id_b"] = merged["trading_account_login_b"].map(self.account_to_user)

        # Filter out same-user matches
        merged = merged[merged["user_id_a"] != merged["user_id_b"]]

        return self._prepare_matches(merged)