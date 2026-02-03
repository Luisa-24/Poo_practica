# ESTANDAR
import pandas as pd
import sys
from pathlib import Path

# LOCALES
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger
from datasets.dataset import Dataset

logger = get_logger(__name__)


class EmployeesDataset(Dataset):
    def __init__(self, source: str):
        super().__init__(Path(source))
        self.obj_list: list[object] = []

    def load_data(self):
        """Load employee data from CSV file and create Employee dataframe.

        Args:
            Path to the source CSV file.

        Returns:
            df_employees: dataframe of loaded Employee objects.

        Raises:
            FileNotFoundError: If the source file does not exist.
        """

        try:
            df_employee = pd.read_csv(self.source)
        except FileNotFoundError:
            raise FileNotFoundError(f"Source file {self.source} not found.")
        except Exception as e:
            raise RuntimeError(f"Error loading CSV: {e}")
        # Rename columns to match EmployeeModel fields
        column_map = {
            "Name": "name",
            "Gender": "gender",
            "Nationality": "nationality",
            "Department": "department",
            "Position": "position",
            "Age": "age",
            "Birthdate": "birthdate",
            "Email": "email",
            "Phone": "phone",
            "Address": "address",
            "Hire Date": "hire_date",
            "Contract Type": "contract_type",
            "Employee ID": "employee_id",
            "Salary": "salary",
            "Termination Date": "termination_date",
        }
        df_employee = df_employee.rename(columns=column_map)
        self.data = df_employee
        return df_employee
