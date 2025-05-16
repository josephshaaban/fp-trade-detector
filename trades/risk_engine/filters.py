from trades.risk_engine.matcher.base_matcher import MatchStrategy


def drop_unnecessary_columns(df):
    columns_to_drop = [
        "pips", "price_tp", "price_sl", "profit", "swap", "contract_size",
        "profit_rate", "platform", "commission", "close_price", "open_price", "reason"
    ]
    return df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors="ignore")

# BONUS: Trade duration must be greater than 1 second
def filter_by_duration(df):
    duration = (df["closed_at"] - df["opened_at"]).dt.total_seconds()
    return df[duration > 1]


# BONUS: Lot size must be ≥ 0.01
def filter_by_lot_size(df):
    return df[df["lot_size"] >= 0.01]