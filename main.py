"""FundingPips Trade Detector Entery Point Module"""

from core.config import load_config, setup_logging
from trades.loader import TradeLoader
import logging


setup_logging()
logger = logging.getLogger("main")

config = load_config()

logger.info(f"Running in Mode {config.mode}")
logger.info(f"Output will be saved to: {config.output_dir}")
logger.debug(f"Data source: {config.data_source.type} @ {config.data_source.path}")

loader = TradeLoader(config)

df = loader.load_trades()
logger.info(f"Trade DataFrame loaded with shape: {df.shape}")
