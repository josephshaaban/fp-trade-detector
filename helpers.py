import pandas as pd
from trades.models import Trade, Account
import logging

logger = logging.getLogger("main")

# Helper method for direction
def trade_direction(trade: Trade) -> str:
    # action 0 = Buy, 1 = Sell
    return "Buy" if trade.action == 0 else "Sell"


def build_account_user_map(accounts: list[Account]) -> dict[int, int]:
    return {acc.login: acc.user_id for acc in accounts}


def join_user_id_to_trades(trades: pd.DataFrame, accounts: pd.DataFrame):
    """
    Join user_id to trades based on trading_account_login.

    This is a vectorized operation that maps the user_id from the
    accounts DataFrame
    instead of using a dict map like `build_account_user_map()`.
    """
    account_user_map = accounts.set_index("login")["user_id"]
    trades["user_id"] = trades["trading_account_login"].map(account_user_map)
    return trades


def time_it(func):
    """Decorator to time the execution of a function."""
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(f"Execution time: {end_time - start_time} seconds")
        return result
    return wrapper
