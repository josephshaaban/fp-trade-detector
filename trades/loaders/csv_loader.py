import numpy as np
import pandas as pd
from pathlib import Path
import logging
from trades.loaders.base_trade_loader import BaseLoader

logger = logging.getLogger("main")

class CSVTradeLoader(BaseLoader):
    def __init__(self, path: Path, parse_dates: list[str] = None):
        super().__init__(path)
        self.parse_dates = parse_dates or []

    def load(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.path}")
        
        logger.info(f"Loading CSV: {self.path}...")

        # Load the CSV and parse dates depending on the dataset
        df = pd.read_csv(
            self.path,
            parse_dates=self.parse_dates
        )
        # handle missing values with None
        df = df.replace({np.nan: None})

        logger.debug(f"Loaded {len(df)} records from {self.path.name}")
        return df