"""Matching and detecting engine for trades."""

from .models import Trade, MatchResult
from typing import List
from datetime import timedelta

from helpers import time_it


def categorize_match(t1: Trade, t2: Trade) -> str:
    if t1.action == t2.action:
        lot_diff_pct = abs(t1.lot_size - t2.lot_size) / max(t1.lot_size, t2.lot_size)
        return "partial" if lot_diff_pct < 0.3 else "copy"
    else:
        return "reverse"


@time_it
def match_trades(trades: List[Trade], mode: str, account_to_user: dict) -> List[MatchResult]:
    matches = []
    trades_by_symbol = {}

    # Group by symbol to reduce comparisons
    for trade in trades:
        trades_by_symbol.setdefault(trade.symbol, []).append(trade)

    for symbol, symbol_trades in trades_by_symbol.items():
        symbol_trades.sort(key=lambda t: t.opened_at)

        for i, t1 in enumerate(symbol_trades):
            for j in range(i + 1, len(symbol_trades)):
                t2 = symbol_trades[j]

                # Stop if beyond 5 minutes
                time_diff = abs((t2.opened_at - t1.opened_at).total_seconds())
                if time_diff > 300:
                    break

                # Skip same account
                if t1.trading_account_login == t2.trading_account_login:
                    continue

                # Skip same-user matches if mode B
                if mode == "B":
                    user1 = account_to_user.get(t1.trading_account_login)
                    user2 = account_to_user.get(t2.trading_account_login)
                    if user1 and user1 == user2:
                        continue

                match_type = categorize_match(t1, t2)
                is_violation = (mode == "B" and match_type in ["copy", "reverse", "partial"])

                matches.append(MatchResult(
                    trade_a=t1,
                    trade_b=t2,
                    category=match_type,
                    time_diff_seconds=time_diff,
                    is_violation=is_violation
                ))

    return matches