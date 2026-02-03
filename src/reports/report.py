# ESTANDAR
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Report(ABC):
    """Generates reports based on data."""

    @abstractmethod
    def generate(self):
        pass
