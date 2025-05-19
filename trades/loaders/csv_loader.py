import numpy as np
import pandas as pd
from pathlib import Path
import logging
from trades.loaders.base_trade_loader import BaseLoader

logger = logging.getLogger("main")


class CSVTradeLoader(BaseLoader):
    def __init__(self, path: Path, parse_dates: list[str] = None, dtype: dict = None):
        super().__init__(path)
        self.parse_dates = parse_dates or []
        self.dtype_dict = dtype

    def load(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.path}")

        logger.info(f"Loading CSV: {self.path}...")

        # Load the CSV and parse dates depending on the dataset
        df = pd.read_csv(
            self.path,
            dtype=self.dtype_dict,
            parse_dates=self.parse_dates,
            na_values=["", "NA", "N/A"],
            keep_default_na=False,
            engine="c",
            on_bad_lines="warn",
        )
        if self.dtype_dict:
            float_cols = df.select_dtypes(include="float32").columns
            df[float_cols] = df[float_cols].astype("Float32")

            df["action"] = pd.to_numeric(df["action"], downcast="integer")
            df["platform"] = pd.to_numeric(df["platform"], downcast="integer")

            df["opened_at"] = pd.to_datetime(
                df["opened_at"],
                format=(
                    "mixed"
                    if df["opened_at"].dt.nanosecond.any()
                    else "%Y-%m-%d %H:%M:%S"
                ),
            )
            df["closed_at"] = pd.to_datetime(
                df["closed_at"],
                format=(
                    "mixed"
                    if df["closed_at"].dt.nanosecond.any()
                    else "%Y-%m-%d %H:%M:%S"
                ),
            )

        # handle missing values with None
        df = df.replace({np.nan: None})

        logger.debug(f"Loaded {len(df)} records from {self.path.name}")
        return df
