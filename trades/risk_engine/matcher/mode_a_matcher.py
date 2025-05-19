import os
import pickle
import numpy as np
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from filelock import FileLock
from multiprocessing import Pool, cpu_count
from datetime import timedelta
from trades.risk_engine.matcher.base_matcher import MatchStrategy
from core import load_config
import logging

# from core.constants import dtype_list, dtype_dict
from trades.risk_engine.categorize import categorize_match


logger = logging.getLogger("main")
SKIPPED_SYMBOLS = [
    "XAUUSD",
]

BATCHED_SYMBOLD = [
    "XAUUSD",
    "EURUSD",
    "NDX100",
    "DJI30",
    "GBPJPY",
    "GBPUSD",
    "GER40",
    "USDJPY",
]


def process_task(task):
    matched_df = match_batch_massive(task)
    return matched_df


def write_results_parallel(tasks, output_file="matches.csv"):
    results_written = False

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(process_task, task) for task in tasks]

        for future in tqdm(
            concurrent.futures.as_completed(futures), total=len(futures)
        ):
            matched_df = future.result()
            if matched_df is not None:
                if not results_written:
                    matched_df.to_csv(output_file, mode="w", index=False)
                    results_written = True
                else:
                    matched_df.to_csv(output_file, mode="a", header=False, index=False)

    print(f"Results written to {output_file}")


def match_batch_massive(args):
    batch, idx, dt_window = args
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"matches.buf")

    dtype = [
        ("opened_at", "datetime64[ns]"),
        ("trading_account_login", "i8"),
        ("identifier", "i8"),
    ]

    mmap_array = np.core.records.fromarrays(
        [batch["opened_at"], batch["trading_account_login"], batch["identifier"]],
        dtype=dtype,
    )

    sorted_indices = np.argsort(mmap_array["opened_at"], kind="mergesort")
    sorted_array = mmap_array[sorted_indices]

    match_dtype = [("identifier_a", "i8"), ("identifier_b", "i8"), ("time_diff", "f4")]
    with open(output_file, "ab") as f:
        buffer = np.empty(100_000, dtype=match_dtype)
        buffer_pos = 0

        timestamps = sorted_array["opened_at"].view("i8")
        window_ns = dt_window * 1e9

        for i in tqdm(range(len(sorted_array))):
            current_time = timestamps[i]
            current_account = sorted_array["trading_account_login"][i]
            current_id = sorted_array["identifier"][i]

            j_max = np.searchsorted(timestamps, current_time + window_ns, side="right")
            mask = (timestamps[i + 1 : j_max] != current_time) & (
                sorted_array["trading_account_login"][i + 1 : j_max] != current_account
            )

            valid_indices = np.where(mask)[0] + i + 1

            if valid_indices.size > 0:
                diffs = (timestamps[valid_indices] - current_time) / 1e9

                ids = sorted_array["identifier"][valid_indices]
                pairs = np.empty(len(ids), dtype=match_dtype)
                pairs["identifier_a"] = np.minimum(current_id, ids)
                pairs["identifier_b"] = np.maximum(current_id, ids)
                pairs["time_diff"] = diffs.astype("f4")

                # Calculate remaining buffer space
                remaining_space = len(buffer) - buffer_pos
                num_pairs = len(pairs)

                # Check if pairs fit in the buffer otherwise fill
                if num_pairs <= remaining_space:
                    
                    buffer[buffer_pos : buffer_pos + num_pairs] = pairs
                    buffer_pos += num_pairs
                else:
                    buffer[buffer_pos:] = pairs[:remaining_space]
                    with FileLock(output_file + ".lock"):
                        buffer.tofile(f)
                    buffer_pos = 0

                    # Handle remaining pairs that didn't fit
                    remaining_pairs = pairs[remaining_space:]
                    if len(remaining_pairs) > 0:
                        if len(remaining_pairs) > len(buffer):
                            buffer[:] = remaining_pairs[: len(buffer)]
                            buffer_pos = len(remaining_pairs) % len(buffer)
                            with FileLock(output_file + ".lock"):
                                remaining_pairs[: len(buffer)].tofile(f)
                        else:
                            buffer[: len(remaining_pairs)] = remaining_pairs
                            buffer_pos = len(remaining_pairs)

                # Flush buffer when full
                if buffer_pos >= len(buffer):
                    with FileLock(output_file + ".lock"):
                        buffer.tofile(f)
                    buffer_pos = 0

        # Flush the last buffer
        if buffer_pos > 0:
            with FileLock(output_file + ".lock"):
                buffer[:buffer_pos].tofile(f)

    return None


def match_batch(args):
    batch, idx, dt_window = args
    batch = batch.sort_values("opened_at").reset_index(drop=True)
    opened_times = batch["opened_at"].values.astype("datetime64[ns]")
    accounts = batch["trading_account_login"].values
    identifiers = batch["identifier"].values

    n = len(batch)
    matched_set = set()

    for i in tqdm(range(n)):
        open_time_a = opened_times[i]
        account_a = accounts[i]
        id_a = identifiers[i]

        t_limit = open_time_a + np.timedelta64(dt_window, "s")

        j = i + 1
        while j < n and opened_times[j] <= t_limit:
            account_b = accounts[j]
            if account_a == account_b:
                j += 1
                continue

            open_time_b = opened_times[j]
            time_diff = (open_time_b - open_time_a) / np.timedelta64(1, "s")
            if time_diff == 0:
                j += 1
                continue

            id_b = identifiers[j]
            pair = (min(id_a, id_b), max(id_a, id_b))
            matched_set.add((pair[0], pair[1], time_diff))
            j += 1

    if matched_set:
        with open(f"match_batch_{idx}.pkl", "wb") as f:
            pickle.dump(matched_set, f)

    return None


def process_matches(matches_file, original_df):
    match_dtype = np.dtype(
        [("identifier_a", "i8"), ("identifier_b", "i8"), ("time_diff", "f4")]
    )
    matches = np.memmap(matches_file, dtype=match_dtype, mode="r")

    # identifier_pairs = matches[['identifier_a', 'identifier_b']]
    # _, unique_indices = np.unique(identifier_pairs, return_index=True, axis=0)
    # del identifier_pairs  # Free memory immediately

    logger.info("Prepare original data...")
    original_df = original_df.astype(
        {"identifier": "Int64", "trading_account_login": "Int64"}
    ).set_index("identifier", drop=True)
    cols = ["opened_at", "closed_at", "action", "lot_size", "trading_account_login"]

    chunk_size = 1_000_000
    chunks = []

    for i in tqdm(range(0, len(matches), chunk_size)):
        # chunk_indices = unique_indices[i:i+chunk_size]
        memmap_chunk = matches[i : i + chunk_size]

        df_chunk = pd.DataFrame(
            {
                "identifier_a": memmap_chunk["identifier_a"],
                "identifier_b": memmap_chunk["identifier_b"],
                "time_diff": memmap_chunk["time_diff"],
            }
        )

        for suffix in ("_a", "_b"):
            df_chunk = df_chunk.merge(
                original_df[cols].add_suffix(suffix),
                left_on=f"identifier{suffix}",
                right_index=True,
                how="left",
            )

        df_chunk["category"] = categorize_match(df_chunk)
        df_chunk = df_chunk[df_chunk["category"] != "unmatched"]
        chunks.append(df_chunk)
        del df_chunk, memmap_chunk

    final_df = pd.concat(chunks, ignore_index=True)
    del chunks, matches

    return final_df


class ModeAStrategy(MatchStrategy):
    def __init__(self, trades: pd.DataFrame, accounts: pd.DataFrame):
        super().__init__(trades, accounts)
        self.name = "Mode A"
        self.mode = "A"

    def _match(self) -> None:
        original_df = self.matched.copy()
        config = load_config()
        dt_window = config.dt_window

        self.matched = self.matched[~self.matched["symbol"].isin(SKIPPED_SYMBOLS)]
        tasks = []
        idx = 0
        for symbol, group in self.matched.groupby("symbol", observed=True):
            df = group.copy()
            logger.debug(f"Processing symbol: {symbol} with {len(df)} rows")

            batched_symbols = set()
            if len(df) > 25_000:
                # batched_symbols.add(symbol)
                logger.warning(
                    f"Symbol `{symbol}` too large ({len(df)} rows). Add to batched symbols."
                )

            if symbol not in batched_symbols:
                tasks.append((df, f"{symbol}", dt_window))
                continue

            df["opened_at"] = pd.to_datetime(df["opened_at"])
            df = df.sort_values("opened_at").reset_index(drop=True)

            desired_batch_size = 20_000
            step = desired_batch_size // 2
            for i in range(0, len(df), step):
                window_anchor = df.iloc[i : i + desired_batch_size]

                window_start = window_anchor["opened_at"].min() - pd.Timedelta(
                    seconds=dt_window
                )
                window_end = window_anchor["opened_at"].max() + pd.Timedelta(
                    seconds=dt_window
                )

                batch = df[
                    (df["opened_at"] >= window_start) & (df["opened_at"] <= window_end)
                ]
                if len(batch) > 25_000:
                    logger.warning(
                        f"Batch for {symbol} {window_start} too large ({len(batch)} rows)"
                    )

                if not batch.empty:
                    idx += 1
                    tasks.append((batch, f"{symbol}-{idx}", dt_window))

        input_dir = "output"
        matches_file = os.path.join(input_dir, f"matches.buf")
        if not os.path.exists(matches_file):
            logger.info("Matches file not found. Generating new matches...")
            write_results_parallel(tasks, output_file="matches.csv")
        else:
            logger.info(f"Using existing matches file: {matches_file}")

        self.matched = process_matches(matches_file, original_df)
        logger.debug(f"Matched trades DataFrame shape: {self.matched.shape}")
