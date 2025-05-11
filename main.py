"""FundingPips Trade Detector Entery Point Module"""

from core import load_config, setup_logging
from trades.loaders.loader_factory import get_loader
from helpers import build_account_user_map
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

    # Convert to models
    trades = [Trade(**row._asdict() if hasattr(row, '_asdict') else row.to_dict()) for _, row in df_trades.iterrows()]
    accounts = [Account(**row._asdict() if hasattr(row, '_asdict') else row.to_dict()) for _, row in df_accounts.iterrows()]

    # Build user map for Mode B
    account_user_map = build_account_user_map(accounts)

    # Run matching
    matches = match_trades(trades, mode=mode, account_to_user=account_user_map)
    logger.info(f"Found {len(matches)} matches")

    for match in matches[:10]:  # preview first 10
        logger.info(
            f"[{match.category.upper()}] {match.trade_a.identifier} <-> {match.trade_b.identifier} | dt={match.time_diff_seconds:.2f}s | Violation={match.is_violation}")


if __name__ == "__main__":
    main()