import pandas as pd
from pathlib import Path
import logging
from trades.loaders.base_trade_loader import BaseTradeLoader

logger = logging.getLogger("main")

class CSVTradeLoader(BaseTradeLoader):
    def load(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.path}")
        logger.info(f"Loading trades from CSV: {self.path}")
        df = pd.read_csv(self.path, parse_dates=["open_time", "close_time"])
        logger.debug(f"Loaded {len(df)} trades from CSV")
        return df