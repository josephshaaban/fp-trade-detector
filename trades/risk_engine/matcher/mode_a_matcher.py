import numpy as np
import pandas as pd
from multiprocessing import Pool, cpu_count
from datetime import timedelta
from trades.risk_engine.matcher.base_matcher import MatchStrategy
from core import load_config
import logging


logger = logging.getLogger("main")
SKIPPED_SYMBOLS = [
    "XAUUSD",
    ]

BATCHED_SYMBOLD = [
    "XAUUSD",
    "EURUSD", "NDX100", "DJI30", "GBPJPY", "GBPUSD", "GER40", "USDJPY",
    ]


def match_batch(args):
    batch, idx, dt_window = args
    batch = batch.sort_values("opened_at").reset_index(drop=True)
    opened_times = batch["opened_at"].values
    n = len(batch)

    seen = set()
    matched_rows = []
    for i in range(n):
        open_time_a = opened_times[i]
        account_a = batch.at[i, "trading_account_login"]
        id_a = batch.at[i, "identifier"]

        t_limit = open_time_a + np.timedelta64(dt_window, "s")
        end_idx = np.searchsorted(opened_times, t_limit, side="right")

        for j in range(i + 1, end_idx):
            account_b = batch.at[j, "trading_account_login"]
            if account_a == account_b:
                continue

            id_b = batch.at[j, "identifier"]
            a, b = (id_a, id_b) if id_a < id_b else (id_b, id_a)
            if (a,b) in seen:
                continue
            seen.add((a,b))

            open_time_b = opened_times[j]
            time_diff = (open_time_b - open_time_a) / np.timedelta64(1, "s")

            matched_rows.append({
                "identifier_a": id_a,
                "identifier_b": id_b,
                "time_diff": time_diff
            })

    if matched_rows:
        # logger.info(f"Matched {len(matched_rows)} trades for window #{idx}"
        #             f" by {i + 1} batches")
        window_matches = pd.DataFrame(matched_rows)
        window_matches = window_matches[
            window_matches["identifier_a"] < window_matches["identifier_b"]]
        return window_matches
    else:
        return None
    
    
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
        batch_size_minutes = 60

        self.matched = self.matched[~self.matched["symbol"].isin(SKIPPED_SYMBOLS)]
        tasks = []
        idx = 0
        for symbol, group in self.matched.groupby("symbol"):
            df = group.copy()
            logger.debug(
                f"Processing symbol: {symbol} with {len(df)} rows")
            
            batched_symbols = set()
            if len(df) > 100_000:
                batched_symbols.add(symbol)
                logger.warning(
                    f"Symbol `{symbol}` too large ({len(df)} rows). Add to batched symbols.")

            if symbol not in batched_symbols:
                tasks.append((df, f"{symbol}", dt_window))
                continue

            df["opened_at"] = pd.to_datetime(df["opened_at"])
            df = df.sort_values("opened_at").reset_index(drop=True)

            start_time = df["opened_at"].min()
            end_time = df["opened_at"].max()


            time_ranges = pd.date_range(
                start=start_time, end=end_time, freq=f"{batch_size_minutes}min")
            for window_anchor in time_ranges:
                window_start = window_anchor - timedelta(minutes=dt_window_minutes)
                window_end = window_anchor + timedelta(
                    minutes=batch_size_minutes + dt_window_minutes)

                batch = df[(df["opened_at"] >= window_start) &
                            (df["opened_at"] <= window_end)]
                if len(batch) > 50_000:
                    logger.warning(
                        f"Batch for {symbol} {window_start} too large ({len(batch)} rows)")
                
                if not batch.empty:
                    idx += 1
                    tasks.append((batch, f"{symbol}-{idx}", dt_window))

        num_processes = min(cpu_count(), len(tasks))
        logger.info(f"Number of jobs: {num_processes}. Number of tasks: {len(tasks)}")
        with Pool(processes=num_processes) as pool:
            results = pool.map(match_batch, tasks)

        results = [df for df in results if df is not None]
        self.matched = pd.concat(
            results, ignore_index=True) if results else pd.DataFrame()
        self.matched["pair_key"] = self.matched.apply(
            lambda row: tuple(sorted((row["identifier_a"], row["identifier_b"]))), axis=1
        )
        self.matched = self.matched.drop_duplicates(subset=["pair_key"]).drop(columns=["pair_key"])
        logger.info(f"Total matches found: {self.matched.shape[0]}")

        columns_to_map = [
            "opened_at", "closed_at", "action", "lot_size", "trading_account_login"]

        original_df.set_index('identifier', inplace=True)
        for suffix in ['a', 'b']:
            id_col = f"identifier_{suffix}"
            for col in columns_to_map:
                self.matched[f'{col}_{suffix}'] = self.matched[id_col].map(
                    original_df[col])
        self.matched["symbol"] = self.matched["identifier_a"].map(
            original_df["symbol"])
        original_df.reset_index(inplace=True)
        
        logger.debug(f"Matched trades DataFrame shape: {self.matched.shape}")
