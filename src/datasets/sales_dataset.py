# ESTANDAR
import pandas as pd
from dataclasses import dataclass
import sys
from pathlib import Path
from typing import List

# LOCALES
sys.path.insert(0, str(Path(__file__).parent.parent))
from datasets.dataset import Dataset
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SalesDataset(Dataset):
    def __init__(self, source: str):
        super().__init__(Path(source))
        self.obj_list: List[object] = []

    def load_data(self):
        """Load sales data from CSV file and create Sales dataframe.

        Args:
            Path to the source CSV file.

        Returns:
            dataframe of loaded Sale objects.

        Raises:
            FileNotFoundError: If the source file does not exist.
        """

        try:
            df_sales = pd.read_csv(self.source)
        except FileNotFoundError:
            raise FileNotFoundError(f"Source file {self.source} not found.")
        except Exception as e:
            raise RuntimeError(f"Error loading CSV: {e}")
        column_map = {
            "Sale ID": "sale_id",
            "Product ID": "product_id",
            "Seller First Name": "seller_first_name",
            "Seller Last Name": "seller_last_name",
            "Seller Employee ID": "seller_employee_id",
            "Buyer Name": "buyer_name",
            "Sale Date": "sale_date",
            "Quantity": "quantity",
            "Unit Price": "unit_price",
            "Total Price": "total_price",
            "Sale Status": "sale_status",
        }
        df_sales = df_sales.rename(columns=column_map)
        self.cleaned_data = df_sales
        return df_sales
