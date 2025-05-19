"""FundingPips Trade Detector Entery Point Module"""

import pandas as pd
import numpy as np
from core import load_config, setup_logging
from trades.loaders.loader_factory import get_loader
from trades.risk_engine.matcher import get_strategy
import logging
from core.constants import dtype_dict

from trades.repoort import generate_pair_report


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


def bonus_filters(strategy):
    """
    Add bonus filters to the strategy.
    """
    from trades.risk_engine.filters import (
        drop_unnecessary_columns,
        filter_by_duration,
        filter_by_lot_size,
    )

    strategy.add_preprocessor(drop_unnecessary_columns)
    strategy.add_preprocessor(filter_by_duration)
    strategy.add_preprocessor(filter_by_lot_size)

    return strategy

def main():
    config = load_config()
    mode = config.mode

    logger.info(f"Running in Mode {config.mode}")
    logger.info(f"Output will be saved to: {config.output_dir}")

    # Load trades data
    trades_loader = get_loader(config, "trades", dtype_dict)
    df_trades = trades_loader.load()
    logger.info(f"Trade DataFrame loaded with shape: {df_trades.shape}")
    df_trades = df_trades.drop_duplicates(subset=['identifier'])
    logger.info(
        f"Trade DataFrame after dropping duplicates with shape: {df_trades.shape}")
    
    logger.debug(
        f"Trade {len(df_trades["symbol"].unique().tolist())} "
        f"symobls: {df_trades["symbol"].unique().tolist().sort()}")

    # Load accounts data
    accounts_loader = get_loader(config, "accounts")
    df_accounts = accounts_loader.load()
    logger.info(f"Account DataFrame loaded with shape: {df_accounts.shape}")

    # Run matching
    strategy = get_strategy(mode, df_trades, df_accounts)
    strategy = bonus_filters(strategy)
    logger.debug(f"Using strategy: {strategy.name}")
    df_matches = strategy.execute()

    # Print some data of matched trades
    logger.info(f"Matched trades DataFrame shape: {df_matches.shape}")
    logger.info(f"Categories found: {df_matches["category"].unique().tolist()}")

    columns_to_display = [
        "trading_account_login_a", "trading_account_login_b"] + [
        col for col in df_matches.columns if col not in [
            "trading_account_login_a", "trading_account_login_b"]]
    print(df_matches[columns_to_display].head())


    pairs = pd.DataFrame({
        "a": np.minimum(df_matches["trading_account_login_a"], df_matches["trading_account_login_b"]),
        "b": np.maximum(df_matches["trading_account_login_a"], df_matches["trading_account_login_b"]),
    })

    pair_counts = pairs.value_counts()
    top_pair = pair_counts.idxmax()
    top_count = pair_counts.max()

    print(f"Most matched pair: {top_pair} with {top_count} matches")
    df_trades.set_index('identifier', inplace=True)
    df_matches["symbol"] = df_matches["identifier_a"].map(df_trades["symbol"])
    df_trades.reset_index(inplace=True)
    # Generate report for the most matched pair
    generate_pair_report(
        df_matches,
        login_a=top_pair[0],
        login_b=top_pair[1],
        output_dir=config.output_dir,
        generate_pdf=False, # see & download: https://wkhtmltopdf.org/downloads.html
    )


if __name__ == "__main__":
    main()