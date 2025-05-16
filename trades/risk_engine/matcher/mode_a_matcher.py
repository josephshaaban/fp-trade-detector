import numpy as np
import pandas as pd
from datetime import timedelta
from trades.risk_engine.matcher.base_matcher import MatchStrategy
from core import load_config
import logging


logger = logging.getLogger("main")
SKIPPED_SYMBOLS = [
    "XAUUSD",
    # "EURUSD", "NDX100", "DJI30", "GBPJPY", "GBPUSD", "GER40", "USDJPY",
    ]

class ModeAStrategy(MatchStrategy):
    def __init__(self, trades: pd.DataFrame, accounts: pd.DataFrame):
        super().__init__(trades, accounts)
        self.name = "Mode A"
        self.mode = "A"

    def _match(self) -> None:
        original_df = self.matched.copy()
        config = load_config()
        dt_window = config.dt_window
        results = []

        for symbol, group in self.matched.groupby("symbol"):
            if symbol in SKIPPED_SYMBOLS:
                continue

            group = group.copy()
            group["opened_at"] = pd.to_datetime(group["opened_at"])
            group = group.sort_values("opened_at").reset_index(drop=True)

            n = len(group)
            opened_times = group["opened_at"].values

            matched_rows = []

            for i in range(n):
                open_time_a = opened_times[i]
                account_a = group.at[i, "trading_account_login"]
                id_a = group.at[i, "identifier"]

                t_limit = open_time_a + np.timedelta64(dt_window, "s")
                end_idx = np.searchsorted(opened_times, t_limit, side="right")

                for j in range(i + 1, end_idx):
                    account_b = group.at[j, "trading_account_login"]
                    if account_a == account_b:
                        continue

                    id_b = group.at[j, "identifier"]
                    open_time_b = opened_times[j]
                    time_diff = (open_time_b - open_time_a) / np.timedelta64(1, "s")

                    matched_rows.append({
                        "identifier_a": id_a,
                        "identifier_b": id_b,
                        "time_diff": time_diff
                    })

            if matched_rows:
                logger.info(f"Matched {len(matched_rows)} trades for symbol {symbol}")
                symbol_matches = pd.DataFrame(matched_rows)
                symbol_matches = symbol_matches[
                    symbol_matches["identifier_a"] < symbol_matches["identifier_b"]]
                results.append(symbol_matches)

        self.matched = pd.concat(
            results, ignore_index=True) if results else pd.DataFrame()
        logger.info(f"Total matches found: {self.matched.shape[0]}")

        columns_to_map = [
            "opened_at", "closed_at", "action", "lot_size", "trading_account_login"]

        original_df.set_index('identifier', inplace=True)
        for suffix in ['a', 'b']:
            id_col = f"identifier_{suffix}"
            for col in columns_to_map:
                self.matched[f'{col}_{suffix}'] = self.matched[id_col].map(
                    original_df[col])
        original_df.reset_index(inplace=True)
        
        logger.debug(f"Matched trades DataFrame shape: {self.matched.shape}")
