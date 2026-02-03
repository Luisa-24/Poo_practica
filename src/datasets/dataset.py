# ESTANDAR
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

# TERCEROS
from pandas import DataFrame


@dataclass
class Dataset(ABC):
    """Abstract base class for datasets.

    Args:
        Path to the data source
    Returns: None
    """

    source: Path
    data: Optional[DataFrame] = field(default=None)

    @abstractmethod
    def load_data(self, source: str):
        """Load data from the specified source."""
        pass
