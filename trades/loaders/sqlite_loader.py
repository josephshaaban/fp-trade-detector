# trades/loaders/sqlite_loader.py
from trades.loaders.base_trade_loader import BaseLoader
import pandas as pd
from pathlib import Path

class SQLiteTradeLoader(BaseLoader):
    def load(self) -> pd.DataFrame:
        raise NotImplementedError("SQLite loading not implemented yet.")
