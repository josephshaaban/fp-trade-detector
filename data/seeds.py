"""Generate Synthetic Data & Inject Controlled Copy/Reverse Trades"""


import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import time

# --- Configuration ---
NUM_TRADES = 1000_000
NUM_INJECTED = 50_000
ACCOUNT_ID_RANGE = (1, 50)
SYMBOLS = ['EURUSD', 'GBPUSD', 'XAUUSD']
DIRECTIONS = ['Buy', 'Sell']
START_TIME = datetime(2023, 1, 1)
CSV_PATH = "data/trades.csv"

faker = Faker()


def generate_random_trade(index: int) -> dict:
    """Generate a base trade with random values."""
    open_time = START_TIME + timedelta(seconds=random.randint(0, 60 * 60 * 24 * 30))  # within 30 days
    duration = timedelta(seconds=random.randint(2, 3600))  # 2s to 1h
    close_time = open_time + duration

    return {
        "ticket": f"T{index}",
        "account_id": random.randint(*ACCOUNT_ID_RANGE),
        "symbol": random.choice(SYMBOLS),
        "direction": random.choice(DIRECTIONS),
        "open_time": open_time,
        "close_time": close_time,
        "lot_size": round(random.uniform(0.01, 5.0), 2),
    }


def generate_matched_trade(original: pd.Series, ticket_index: int) -> dict:
    """Inject a matched trade (copy, reverse, partial copy) for detection testing."""
    # New account different from original
    new_account = original.account_id
    while new_account == original.account_id:
        new_account = random.randint(*ACCOUNT_ID_RANGE)

    # Open/close time within +_5 minutes of original
    offset = timedelta(seconds=random.randint(-300, 300))
    open_time = original.open_time + offset
    duration = original.close_time - original.open_time
    close_time = open_time + duration

    # Select match type
    match_type = random.choice(["copy", "reverse", "partial"])

    direction = original.direction
    lot_size = original.lot_size

    if match_type == "reverse":
        direction = "Sell" if original.direction == "Buy" else "Buy"
    elif match_type == "partial":
        lot_size = round(original.lot_size * random.uniform(0.75, 1.25), 2)

    return {
        "ticket": f"T{ticket_index}",
        "account_id": new_account,
        "symbol": original.symbol,
        "direction": direction,
        "open_time": open_time,
        "close_time": close_time,
        "lot_size": lot_size,
    }


def create_synthetic_trades(num_base: int, num_injected: int) -> pd.DataFrame:
    """Generate full synthetic dataset with injected matches."""
    base_trades = [generate_random_trade(i) for i in range(num_base)]
    df_base = pd.DataFrame(base_trades)

    injected = [
        generate_matched_trade(df_base.sample(1).iloc[0], num_base + i)
        for i in range(num_injected)
    ]
    df_injected = pd.DataFrame(injected)

    return pd.concat([df_base, df_injected], ignore_index=True)


def save_trades(df: pd.DataFrame, path: str) -> None:
    """Save trades to CSV."""
    df.to_csv(path, index=False)


if __name__ == "__main__":
    # A timer to measure the execution time
    start_time = time.time()
    df_trades = create_synthetic_trades(NUM_TRADES, NUM_INJECTED)
    save_trades(df_trades, CSV_PATH)
    end_time = time.time()

    # while developing use less number of records
    # Generated 100500 trades. Saved to: trades.csv
    # Execution time: 2.75 seconds
    # Generated 1050000 trades. Saved to: trades.csv
    # Execution time: 1246.29 seconds
    print(f"Generated {len(df_trades)} trades. Saved to: {CSV_PATH}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
