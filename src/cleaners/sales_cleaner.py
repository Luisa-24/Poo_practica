# ESTÁNDAR
import pandas as pd
import sys
from pathlib import Path

# LOCALES
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger

logger = get_logger(__name__)


def clean_data(sales_df: pd.DataFrame, employees_df: pd.DataFrame):
    """
    Cleans sales data, ensuring that each sale's
    date is after the seller's hire date. If not, reassigns
    the sale to a valid employee (with hire_date menor o igual a sale_date).

    Args:
        DataFrame with sales data.
        DataFrame with employee data.
    Returns:
        Cleaned sales DataFrame.
    """
    # Validate existence of required columns
    required_sales_cols = ["sale_date", "seller_employee_id"]
    required_employee_cols = ["employee_id", "hire_date"]
    missing_sales = [col for col in required_sales_cols if col not in sales_df.columns]
    missing_emps = [
        col for col in required_employee_cols if col not in employees_df.columns
    ]
    if missing_sales:
        logger.warning(f"Missing columns in sales DataFrame: {missing_sales}")
        return sales_df
    if missing_emps:
        logger.warning(f"Missing columns in employees DataFrame: {missing_emps}")
        return sales_df

    # Validate type of date columns
    sales_df = ensure_datetime(sales_df, "sale_date")
    employees_df = ensure_datetime(employees_df, "hire_date")

    # Join sales with employees to verify dates
    merged = sales_df.merge(
        employees_df[["employee_id", "hire_date"]],
        left_on="seller_employee_id",
        right_on="employee_id",
        how="left",
        suffixes=("", "_emp"),
    )

    # Identify invalid sales
    invalid_mask = merged["sale_date"] < merged["hire_date"]
    invalid_sales_idx = merged[invalid_mask].index

    # Reassign invalid sales
    for idx in invalid_sales_idx:
        sale_row = merged.loc[idx]
        valid_emps = employees_df[employees_df["hire_date"] <= sale_row["sale_date"]]
        if not valid_emps.empty:
            # Assign the first valid employee found
            new_emp_id = valid_emps.iloc[0]["employee_id"]
            sales_df.at[idx, "seller_employee_id"] = new_emp_id
        # If no valid employee, the sale remains unchanged

    return sales_df


def ensure_datetime(df: pd.DataFrame, col: str):
    """
    Converts a column to datetime if it is not already.

    Args:
        Input DataFrame.
        Name of the column to convert.
    Returns:
        DataFrame with the converted column.
    """
    if not pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df
