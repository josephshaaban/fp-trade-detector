"""Defines Trades Models"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal


class Account(BaseModel):
    login: int
    account_size: int
    platform: int
    phase: int
    user_id: int
    challenge_id: int


class Trade(BaseModel):
    identifier: int
    trading_account_login: int
    action: int
    reason: Optional[int]
    symbol: str
    open_price: float
    close_price: float
    commission: float
    lot_size: float
    opened_at: datetime
    closed_at: datetime
    pips: Optional[float]
    price_sl: Optional[float]
    price_tp: Optional[float]
    profit: float
    swap: float
    contract_size: float
    profit_rate: Optional[float]
    platform: int

    @property
    def direction(self) -> str:
        """Returns the direction of the trade."""
        from helpers import trade_direction
        return trade_direction(self)




class MatchResult(BaseModel):
    trade_a: Trade
    trade_b: Trade
    category: Literal["copy", "reverse", "partial"]
    time_diff_seconds: float
    is_violation: bool