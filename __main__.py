import json
import sys
import os

# Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


from concurrent.futures import ThreadPoolExecutor
from utils.logger import setup_logging, get_logger
from utils.progress import pipeline_progress
from cleaners.employees_cleaner import clean_data as clean_employees
from cleaners.sales_cleaner import clean_data as clean_sales
from validators.employees_validator import validate_employees
from validators.sales_validator import validate_sales
from datasets.employees_dataset import EmployeesDataset
from datasets.sales_dataset import SalesDataset
from objects.employee import Employee
from objects.sale import Sale
from reports.fill_template import generate_employees_pdf, generate_sales_pdf
from relations.Relations import RelationsValidator

logger = None


def load_config():
    """Load configuration from JSON file."""
    with open("configs/configs.json", "r") as f:
        return json.load(f)


def create_employee_instances(df_employees, validations):
    """Create Employee instances from valid rows."""
    valid_mask = ~validations.eq(False).any(axis=1)
    valid_employees = df_employees[valid_mask]

    fields = [
        "_name",
        "_gender",
        "_nationality",
        "_department",
        "_position",
        "_age",
        "_birthdate",
        "_email",
        "_phone",
        "_address",
        "_hire_date",
        "_contract_type",
        "_employee_id",
        "_salary",
        "_termination_date",]

    return [
        Employee(**{f: row.get(f[1:]) for f in fields}) 
        for row in valid_employees.to_dict(orient="records")
    ]


def create_sale_instances(df_sales, validations):
    """Create Sale instances from valid rows."""
    valid_mask = ~validations.eq(False).any(axis=1)
    return [Sale(**row) for row in df_sales[valid_mask].to_dict(orient="records")]


def save_csv_reports(df_employees_clean, df_sales_clean, config):
    """Save cleaned DataFrames to CSV files."""
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(
            lambda: df_employees_clean.to_csv(
                config["cleaned_employee_data_path"], index=False))
        executor.submit(
            lambda: df_sales_clean.to_csv(
                config["cleaned_sales_data_path"], index=False))


def calculate_relations(df_employees_clean, df_sales_clean):
    """Calculate relations between employees and sales datasets."""
    emp = df_employees_clean.copy()
    emp["Employee ID"] = emp["employee_id"]
    emp["First Name"] = emp["name"].apply(lambda x: str(x).split()[0] if x else "")
    emp["Last Name"] = emp["name"].apply(
        lambda x: " ".join(str(x).split()[1:]) if x and len(str(x).split()) > 1 else "")

    sales = df_sales_clean.copy()
    sales["Seller Employee ID"] = sales["seller_employee_id"]
    sales["Seller First Name"] = sales.get("seller_first_name", "")
    sales["Seller Last Name"] = sales.get("seller_last_name", "")

    validator = RelationsValidator(emp, sales)
    emp_sin_ventas = validator.validate_count_employees_without_sales()

    return {
        "employees_without_sales": emp_sin_ventas,
        "employees_with_sales": len(df_employees_clean) - emp_sin_ventas,
        "invalid_employee_ids_in_sales": len(
            validator.validate_employee_ids_in_sales()),
        "invalid_names_in_sales": len(validator.validate_employee_names_in_sales()),
        "sales_with_valid_employee": len(df_sales_clean)
        - len(validator.validate_employee_ids_in_sales()),
        "sales_with_invalid_employee": len(validator.validate_employee_ids_in_sales()),
        "sales_reassigned": 0, }


def main():
    """Main pipeline function."""
    global logger
    config = load_config()
    setup_logging(config.get("log_level", "INFO"))
    logger = get_logger(__name__)

    with pipeline_progress() as progress:

        # Load data
        progress.start_phase("Loading Data", total=2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            df_employees = executor.submit(
                lambda: EmployeesDataset(config["employee_data_path"]).load_data()).result()
            progress.advance("Loading Data")
            df_sales = executor.submit(
                lambda: SalesDataset(config["sales_data_path"]).load_data()).result()
            progress.advance("Loading Data")

        progress.complete_phase("Loading Data")
        progress.set_stat("Employees loaded", len(df_employees))
        progress.set_stat("Sales loaded", len(df_sales))

        # Clean data
        progress.start_phase("Cleaning Data", total=2)
        df_employees_clean = clean_employees(df_employees)
        progress.advance("Cleaning Data")
        df_sales_clean = clean_sales(df_sales, df_employees_clean)
        progress.advance("Cleaning Data")
        progress.complete_phase("Cleaning Data")

        # Validate data
        progress.start_phase("Validating Data", total=2)
        with ThreadPoolExecutor(max_workers=2) as executor:
            employee_validations = executor.submit(
                validate_employees, df_employees_clean.to_dict(orient="records")).result()
            progress.advance("Validating Data")
            sales_validations = executor.submit(
                validate_sales, df_sales_clean.to_dict(orient="records")).result()
            progress.advance("Validating Data")
        progress.complete_phase("Validating Data")

        # Create instances
        progress.start_phase("Creating Instances", total=2)
        employees = create_employee_instances(df_employees_clean, employee_validations)
        progress.advance("Creating Instances")
        sales = create_sale_instances(df_sales_clean, sales_validations)
        progress.advance("Creating Instances")
        progress.complete_phase("Creating Instances")
        progress.set_stat("Valid employees", len(employees))
        progress.set_stat("Valid sales", len(sales))

        # Calculate relations
        progress.start_phase("Calculating Relations")
        relation_stats = calculate_relations(df_employees_clean, df_sales_clean)
        progress.complete_phase("Calculating Relations")
        progress.set_stat(
            "Employees without sales", relation_stats["employees_without_sales"])

        # Stats for reports
        cleaning_stats_emp = {
            "emails_cleaned": len(df_employees_clean)
            if "email" in df_employees_clean.columns
            else 0,
            "phones_cleaned": len(df_employees_clean)
            if "phone" in df_employees_clean.columns
            else 0,
            "genders_inferred": len(df_employees_clean)
            if "gender" in df_employees_clean.columns
            else 0, }
        cleaning_stats_sales = {"sales_reassigned": 0, "dates_corrected": 0}

        # Save CSV reports
        progress.start_phase("Saving CSV Reports")
        save_csv_reports(df_employees_clean, df_sales_clean, config)
        progress.complete_phase("Saving CSV Reports")

        # Generate PDF reports
        progress.start_phase("Generating PDF Reports", total=2)
        try:
            generate_employees_pdf(
                df_employees,
                df_employees_clean,
                employee_validations,
                len(df_employees_clean),
                cleaning_stats_emp,
                relation_stats,
                "src/reports/output",)
            progress.advance("Generating PDF Reports")
        except Exception as e:
            progress.advance("Generating PDF Reports")
            progress.log_warning(f"Could not generate employees PDF: {e}")

        try:
            generate_sales_pdf(
                df_sales,
                df_sales_clean,
                sales_validations,
                len(df_sales_clean),
                cleaning_stats_sales,
                relation_stats,
                "src/reports/output",
            )
            progress.advance("Generating PDF Reports")
        except Exception as e:
            progress.advance("Generating PDF Reports")
            progress.log_warning(f"Could not generate sales PDF: {e}")
        progress.complete_phase("Generating PDF Reports")


if __name__ == "__main__":
    main()
