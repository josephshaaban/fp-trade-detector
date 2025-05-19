"""Load + preprocess CSV/JSON/DB trades into a DataFrame.

This module provides functions to load trades from various sources, including CSV files.
"""

from core.config import AppConfig
from pathlib import Path
from typing import Dict
from trades.loaders.csv_loader import CSVTradeLoader
from trades.loaders.sqlite_loader import SQLiteTradeLoader
from trades.loaders.base_trade_loader import BaseLoader

def get_loader(config: AppConfig, dataset: str, dtype: Dict = None) -> BaseLoader:
    if dataset not in config.data_sources:
        raise KeyError(f"No data source config found for dataset: {dataset}")
    
    ds_config = config.data_sources[dataset]
    path = Path(ds_config.path)
    loader_type = ds_config.type.lower()

    if loader_type == "csv":
        return CSVTradeLoader(path, parse_dates=ds_config.parse_dates, dtype=dtype)
    elif loader_type == "sqlite":
        return SQLiteTradeLoader(path)
    else:
        raise ValueError(f"Unsupported data source type: {loader_type}")
