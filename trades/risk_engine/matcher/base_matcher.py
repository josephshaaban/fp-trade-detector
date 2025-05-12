import pandas as pd
from abc import ABC, abstractmethod
from trades.risk_engine.categorize import categorize_match


class MatchStrategy(ABC):
    def __init__(self, trades: pd.DataFrame, accounts: pd.DataFrame):
        self.trades = trades
        self.accounts = accounts
        self.account_to_user = accounts.set_index("login")["user_id"]
        self.matched: pd.DataFrame = self.trades.copy()
        self.name = "Base"
        self.mode = None
        self.preprocessors = []     # before matching
        self.postprocessors = []    # after matching

    @abstractmethod
    def _match(self) -> None:
        pass

    def execute(self) -> pd.DataFrame:
        # Apply preprocessors
        for processor in self.preprocessors:
            self.matched = processor(self.matched)

        # Perform matching
        self._match()
        # Common postprocessing
        self._prepare_matches()

        # Apply postprocessors
        for processor in self.postprocessors:
            self.matched = processor(self.matched)

        return self.matched

    def _prepare_matches(self) -> None:
        df = self.matched.copy()

        # Categorize matches
        df["category"] = categorize_match(df)

        self.matched = df
    
    def add_preprocessor(self, processor: callable) -> None:
        self.preprocessors.append(processor)
    
    def add_postprocessor(self, processor: callable) -> None:
        self.postprocessors.append(processor)