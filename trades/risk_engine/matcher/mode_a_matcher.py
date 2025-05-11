import pandas as pd
from .base_matcher import MatchStrategy


class ModeAStrategy(MatchStrategy):
    def match(self) -> pd.DataFrame:
        raise NotImplementedError("Mode A matching is not implemented yet.")