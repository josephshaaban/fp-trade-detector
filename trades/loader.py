"""Load + preprocess CSV/JSON/DB trades into a DataFrame.

This module provides functions to load trades from various sources, including CSV files.
"""

import logging
import pandas as pd
from pathlib import Path
from core.config import AppConfig

logger = logging.getLogger("mian")


class TradeLoader:
    """Service class to load trades from different data sources."""

    def __init__(self, config: AppConfig):
        self.config = config

    def load_trades(self) -> pd.DataFrame:
        """Main entrypoint: Load trades based on config source."""
        source_type = self.config.data_source.type.lower()
        source_path = Path(self.config.data_source.path)

        if source_type == "csv":
            return self._load_csv(source_path)
        elif source_type == "sqlite":
            return self._load_sqlite(source_path)
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")

    def _load_csv(self, path: Path) -> pd.DataFrame:
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")
        logger.info(f"Loading trades from CSV: {path}")
        df = pd.read_csv(path, parse_dates=["open_time", "close_time"])
        logger.debug(f"Loaded {len(df)} trades from CSV")
        return df

    def _load_sqlite(self, path: Path) -> pd.DataFrame:
        raise NotImplementedError("SQLite loading not yet implemented.")
