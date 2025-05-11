from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path

class BaseLoader(ABC):
    def __init__(self, path: Path):
        self.path = path

    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass
