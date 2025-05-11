import pandas as pd
from .base_matcher import MatchStrategy


class ModeBStrategy(MatchStrategy):
    def match(self) -> pd.DataFrame:
        raise NotImplementedError("Mode B matching is not implemented yet.")