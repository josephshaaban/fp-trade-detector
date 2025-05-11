import pandas as pd
import numpy as np


def categorize_match(df: pd.DataFrame) -> pd.Series:
    same_direction = df["action_a"] == df["action_b"]
    lot_diff = np.abs(df["lot_size_a"] - df["lot_size_b"])
    lot_max = np.maximum(df["lot_size_a"], df["lot_size_b"])
    lot_diff_pct = lot_diff / lot_max

    conditions = [
        same_direction & (lot_diff_pct < 0.3),
        same_direction,
        ~same_direction,
    ]
    choices = ["partial", "copy", "reverse"]

    default_value = "unmatched"

    return np.select(conditions, choices, default=default_value)
