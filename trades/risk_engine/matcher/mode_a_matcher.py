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
        dt_window_minutes = dt_window / 60
        batch_size_minutes = 15
        results = []

        df = self.matched.copy()
        df["opened_at"] = pd.to_datetime(df["opened_at"])
        df = df.sort_values("opened_at").reset_index(drop=True)

        start_time = df["opened_at"].min()
        end_time = df["opened_at"].max()

        time_ranges = pd.date_range(
            start=start_time, end=end_time, freq=f"{batch_size_minutes}min")
        n_time_ranges = len(time_ranges)

        for idx, window_start in enumerate(time_ranges):
            window_end = window_start + timedelta(
                minutes=batch_size_minutes + dt_window_minutes)

            batch_df = df[
                (df["opened_at"] >= window_start - timedelta(minutes=dt_window_minutes)) &
                (df["opened_at"] <= window_end)
                ].copy()
            
            if batch_df.empty:
                continue

            batch_df = batch_df.sort_values("opened_at").reset_index(drop=True)
            opened_times = batch_df["opened_at"].values
            n = len(batch_df)

            matched_rows = []

            for i in range(n):
                open_time_a = opened_times[i]
                account_a = batch_df.at[i, "trading_account_login"]
                id_a = batch_df.at[i, "identifier"]

                t_limit = open_time_a + np.timedelta64(dt_window, "s")
                end_idx = np.searchsorted(opened_times, t_limit, side="right")

                for j in range(i + 1, end_idx):
                    account_b = batch_df.at[j, "trading_account_login"]
                    if account_a == account_b:
                        continue

                    id_b = batch_df.at[j, "identifier"]
                    open_time_b = opened_times[j]
                    time_diff = (open_time_b - open_time_a) / np.timedelta64(1, "s")

                    matched_rows.append({
                        "identifier_a": id_a,
                        "identifier_b": id_b,
                        "time_diff": time_diff
                    })

            if matched_rows:
                logger.info(f"Matched {len(matched_rows)} trades for window {idx + 1}"
                            f"/{n_time_ranges} by {i} batches")
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
