"""FundingPips Trade Detector Entery Point Module"""

from core import load_config, setup_logging
from trades.loaders.loader_factory import get_loader
from helpers import join_user_id_to_trades
from trades.models import Trade, Account
from trades.matcher import match_trades
import logging


setup_logging()
logger = logging.getLogger("main")


def discover_datasets(df_trades, df_accounts):
    from data.discover_data import discover_dataframe
    from pprint import pprint
    # accounts
    account_report = discover_dataframe(
        df_accounts,
        name="Accounts",
        key_columns=["login", "user_id"],
        numeric_columns=[],
        categorical_columns=["platform", "phase", "account_size"]
    )
    pprint(account_report)

    # trades
    trade_report = discover_dataframe(
        df_trades,
        name="Trades",
        key_columns=["identifier", "trading_account_login"],
        numeric_columns=["lot_size", "commission", "open_price", "close_price"],
        categorical_columns=["symbol", "platform"]
    )
    pprint(trade_report)


def main():
    config = load_config()
    mode = config.mode

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

    # Build user map for Mode B
    df_trades = join_user_id_to_trades(df_trades, df_accounts)

    # TODO: Run matching
    # matches = match_trades(trades, mode=mode, account_to_user=account_user_map)
    # logger.info(f"Found {len(matches)} matches")

    # Print the first 5 rows of df_trades
    print(df_trades.head())


if __name__ == "__main__":
    main()