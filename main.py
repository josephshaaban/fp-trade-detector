"""FundingPips Trade Detector Entery Point Module"""

from core import load_config, setup_logging
from trades.loaders.loader_factory import get_loader
import logging


setup_logging()
logger = logging.getLogger("main")

config = load_config()

logger.info(f"Running in Mode {config.mode}")
logger.info(f"Output will be saved to: {config.output_dir}")

# Load trades data
trades_loader = get_loader(config, "trades")
df_trades = trades_loader.load()
logger.info(f"Trade DataFrame loaded with shape: {df_trades.shape}")

# Load accounts data
accounts_loader = get_loader(config, "accounts")
df_accounts = accounts_loader.load()
logger.info(f"Account DataFrame loaded with shape: {df_accounts.shape}")
