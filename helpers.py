from trades.models import Trade, Account
import logging

logger = logging.getLogger("main")

# Helper method for direction
def trade_direction(trade: Trade) -> str:
    # action 0 = Buy, 1 = Sell
    return "Buy" if trade.action == 0 else "Sell"


def build_account_user_map(accounts: list[Account]) -> dict[int, int]:
    return {acc.login: acc.user_id for acc in accounts}


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
