# ESTANDAR
import pandas as pd
from dataclasses import dataclass
import sys
from pathlib import Path

# LOCALES
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RelationsValidator:
    """
    Validate relations and consistency between datasets, such as employees and sales.

    Args: DataFrames of employees and sales.
    Returns: Various validation results as DataFrames or counts.
    """

    employees_df: pd.DataFrame
    sales_df: pd.DataFrame

    def validate_employee_without_sales(self):
        """
        Verify that all employees have at least one associated sale.

        Args: None
        Returns: DataFrame with employees without sales.
        """

        logger.info("Executing validate_employee_without_sales...")
        merged_df = pd.merge(
            self.employees_df,
            self.sales_df,
            left_on="Employee ID",
            right_on="Seller Employee ID",
            how="left",
            indicator=True,
        )

        employees_no_sales = merged_df[merged_df["_merge"] == "left_only"]
        logger.info(
            "Validation completed: %d employees without sales", len(employees_no_sales)
        )
        return employees_no_sales[["Employee ID", "First Name", "Last Name"]]

    def validate_employee_ids_in_sales(self):
        """
        Verify that all seller_employee_id in sales
        exist in employee_id of the data employees.

        Args: None
        Returns: DataFrame with sales having invalid IDs.
        """

        logger.info("Executing validate_employee_ids_in_sales...")
        valid_ids = set(self.employees_df["Employee ID"])
        invalid_sales = self.sales_df[
            ~self.sales_df["Seller Employee ID"].isin(valid_ids)
        ]
        logger.info("Validation completed: %d invalid sales found", len(invalid_sales))
        return invalid_sales

    def validate_count_employees_without_sales(self):
        """Count the number of employees without associated sales.

        Args: None
        Returns: Integer with the count of employees without sales.
        """

        logger.info("Executing validate_count_employees_without_sales...")
        merged_df = pd.merge(
            self.employees_df,
            self.sales_df,
            left_on="Employee ID",
            right_on="Seller Employee ID",
            how="left",
            indicator=True,
        )

        employees_no_sales = merged_df[merged_df["_merge"] == "left_only"]
        count_no_sales = len(employees_no_sales)
        logger.info(f"Validation completed: {count_no_sales} employees without sales")
        return count_no_sales

    def validate_employee_names_in_sales(self):

        """
        Verify that seller names in sales match
        the registered employee names.

        Args: None
        Returns: DataFrame with sales where the name does not match.
        """
        logger.info("Executing validate_employee_names_in_sales...")

        valid_names = set(
            zip(
                self.employees_df["First Name"].str.lower().str.strip(),
                self.employees_df["Last Name"].str.lower().str.strip(),
            )
        )

        def is_valid_name(row):
            """ Verify if the seller's name matches a valid employee name.

             Args:
                row: A row from the sales DataFrame.
             Returns:
                bool: True if the name matches, False otherwise."""

            first = str(row.get("Seller First Name", "")).lower().strip()
            last = str(row.get("Seller Last Name", "")).lower().strip()
            return (first, last) in valid_names

        invalid_sales = self.sales_df[~self.sales_df.apply(is_valid_name, axis=1)]

        logger.info(
            "Validation completed: %d sales with invalid names", len(invalid_sales)
        )
        return invalid_sales
