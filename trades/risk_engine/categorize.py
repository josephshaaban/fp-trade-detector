import pandas as pd
import numpy as np


def categorize_match(df: pd.DataFrame) -> pd.Series:
    same_direction = df["action_a"] == df["action_b"]
    opposite_direction = ~same_direction

    lot_equal = df["lot_size_a"] == df["lot_size_b"]
    lot_diff = np.abs(df["lot_size_a"] - df["lot_size_b"])
    lot_max = np.maximum(df["lot_size_a"], df["lot_size_b"])
    lot_diff_pct = lot_diff / lot_max

    # Flag unmatched to drop later
    category = np.full(len(df), "unmatched", dtype=object)

    category[same_direction & (lot_diff_pct < 0.3) & ~lot_equal] = "partial"
    category[same_direction & lot_equal] = "copy"
    category[opposite_direction & lot_equal] = "reverse"

    return pd.Series(category, index=df.index)
