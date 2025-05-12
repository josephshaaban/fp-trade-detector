import pandas as pd
from datetime import timedelta
from trades.risk_engine.matcher.base_matcher import MatchStrategy
from core import load_config


class ModeAStrategy(MatchStrategy):
    def __init__(self, trades: pd.DataFrame, accounts: pd.DataFrame):
        super().__init__(trades, accounts)
        self.name = "Mode A"
        self.mode = "A"

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
            results.append(merged)

        final_merged = pd.concat(results, ignore_index=True)

        self.matched = final_merged.copy()