"""Load + preprocess CSV/JSON/DB trades into a DataFrame.

This module provides functions to load trades from various sources, including CSV files.
"""

from core.config import AppConfig
from pathlib import Path
from trades.loaders.csv_loader import CSVTradeLoader
from trades.loaders.sqlite_loader import SQLiteTradeLoader
from trades.loaders.base_trade_loader import BaseTradeLoader

def get_loader(config: AppConfig) -> BaseTradeLoader:
    path = Path(config.data_source.path)
    loader_type = config.data_source.type.lower()

    if loader_type == "csv":
        return CSVTradeLoader(path)
    elif loader_type == "sqlite":
        return SQLiteTradeLoader(path)
    else:
        raise ValueError(f"Unsupported data source type: {loader_type}")
