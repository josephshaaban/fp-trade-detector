import pandas as pd
from abc import ABC, abstractmethod
from trades.risk_engine.categorize import categorize_match


class MatchStrategy(ABC):
    def __init__(self, trades: pd.DataFrame, accounts: pd.DataFrame):
        self.trades = trades
        self.accounts = accounts
        self.account_to_user = accounts.set_index("login")["user_id"]

    @abstractmethod
    def match(self) -> pd.DataFrame:
        pass

    def _prepare_matches(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Ensure time diff is within 5 minutes
        df["time_diff"] = (df["opened_at_b"] - df["opened_at_a"]).dt.total_seconds().abs()
        df = df[df["time_diff"] <= 300]

        # Remove same-account matches
        df = df[df["trading_account_login_a"] != df["trading_account_login_b"]]

        # Categorize matches
        df["category"] = categorize_match(df)
        return df