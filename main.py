"""FundingPips Trade Detector Entery Point Module"""

from core.config import load_config, setup_logging
from trades.loaders.loader_factory import get_loader
import logging


setup_logging()
logger = logging.getLogger("main")

config = load_config()

logger.info(f"Running in Mode {config.mode}")
logger.info(f"Output will be saved to: {config.output_dir}")
logger.debug(f"Data source: {config.data_source.type} @ {config.data_source.path}")

loader = get_loader(config)

df = loader.load()
logger.info(f"Trade DataFrame loaded with shape: {df.shape}")
