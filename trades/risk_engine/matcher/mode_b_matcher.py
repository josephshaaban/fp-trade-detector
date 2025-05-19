import pandas as pd
from core import load_config
from .mode_a_matcher import ModeAStrategy


class ModeBStrategy(ModeAStrategy):
    def __init__(self, trades: pd.DataFrame, accounts: pd.DataFrame):
        super().__init__(trades, accounts)
        self.name = "Mode B"
        self.mode = "B"
        self.add_postprocessor(self.add_violation_flag)

    @staticmethod
    def add_violation_flag(df: pd.DataFrame) -> pd.DataFrame:
        df["is_violation"] = (
            df["category"].isin(["copy", "reverse", "partial"])
        ) & (df["user_id_a"] == df["user_id_b"])
        return df
    
    def _match(self) -> None:
        super()._match()
        matched_df = self.matched.copy()
        matched_df["user_id_a"] = matched_df["trading_account_login_a"].map(self.account_to_user)
        matched_df["user_id_b"] = matched_df["trading_account_login_b"].map(self.account_to_user)

        # matched_df = matched_df[matched_df["user_id_a"] == matched_df["user_id_b"]]
        self.matched = matched_df.copy()