# ESTÁNDAR
import sys
import os

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from datasets.dataset import Dataset


class DummyDataset(Dataset):
    def load_data(self, source: str):
        return f"Loaded from {source}"

    def save_data(self, destination: str):
        return f"Saved to {destination}"


def test_dataset_instantiation():
    dummy = DummyDataset(source="dummy.csv")
    assert dummy.load_data("dummy.csv") == "Loaded from dummy.csv"
    assert dummy.save_data("dest.csv") == "Saved to dest.csv"
