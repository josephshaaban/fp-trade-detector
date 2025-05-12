import pandas as pd
from core import load_config
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
    
    def _match(self) -> None:
        config = load_config()
        dt_window = config.dt_window
        results = []
        for symbol, group in self.matched.groupby("symbol"):
            group = group.copy()
            group["opened_at"] = pd.to_datetime(group["opened_at"])
            group = group.sort_values("opened_at").reset_index(drop=True)
            
            group = group.reset_index(drop=True)
            # Use broadcasting: expand to Cartesian product (cross join)
            left = group.rename(columns=lambda x: f"{x}_a")
            right = group.rename(columns=lambda x: f"{x}_b")
            
            merged = left.merge(right, how='cross')
            
            # Ensure time diff is within 5 minutes
            merged["time_diff"] = (
                merged["opened_at_b"] - merged["opened_at_a"]
                ).dt.total_seconds().abs()
            
            merged = merged[
                # Remove same-account matches
                (merged['trading_account_login_a'] != merged['trading_account_login_b']) &
                # Filter rows not matching time diff
                (merged["time_diff"] <= dt_window)
            ]

            merged = merged[merged["identifier_a"] < merged["identifier_b"]]

            # Inject user_ids for filtering
            merged["user_id_a"] = merged["trading_account_login_a"].map(self.account_to_user)
            merged["user_id_b"] = merged["trading_account_login_b"].map(self.account_to_user)

            # Filter out same-user matches
            merged = merged[merged["user_id_a"] != merged["user_id_b"]]
            
            results.append(merged)

        final_merged = pd.concat(results, ignore_index=True)
        self.matched = final_merged.copy()