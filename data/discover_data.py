import pandas as pd
from typing import List, Optional, Tuple


def discover_dataframe(
    df: pd.DataFrame,
    name: str,
    key_columns: Optional[List[str]] = None,
    numeric_columns: Optional[List[str]] = None,
    categorical_columns: Optional[List[str]] = None,
) -> dict:
    """Analyze structure, uniqueness, value ranges, and missingness in a DataFrame."""
    print(f"\n Discovering: {name}")
    report = {}

    # General info
    report["rows"] = len(df)
    report["columns"] = df.columns.tolist()

    # Uniqueness
    if key_columns:
        for col in key_columns:
            report[f"{col}_unique_count"] = df[col].nunique()

        if len(key_columns) > 1:
            report["key_pair_duplicates"] = df.duplicated(subset=key_columns).sum()

    # Numeric stats
    if numeric_columns:
        report["numeric_stats"] = df[numeric_columns].describe()

    # Categorical summaries
    if categorical_columns:
        for col in categorical_columns:
            report[f"{col}_unique_values"] = df[col].unique().tolist()

    # Nulls
    report["missing_per_column"] = df.isnull().sum()
    
    return report

