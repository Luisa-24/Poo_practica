# ESTANDAR
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import pandas as pd

# LOCALES
from .report import Report


@dataclass
class EmployeesReport(Report):
    """Class to manage employee report data.

    Args: Various data related to employee reports.
    Returns: Structured employee report data"""

    df_original: pd.DataFrame
    df_clean: pd.DataFrame
    validations: pd.DataFrame
    employees_created: int
    cleaning_stats: Optional[Dict[str, Any]] = field(default_factory=dict)
    relation_stats: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        if self.cleaning_stats is None:
            self.cleaning_stats = {}
        if self.relation_stats is None:
            self.relation_stats = {}
        self._calculate_stats()

    def _calculate_stats(self):
        """Calculates statistics for the employee dataset."""
        # Basic statistics
        self.total_original = len(self.df_original)
        self.total_clean = len(self.df_clean)

        # Total valid = total clean (successfully processed records)
        self.total_valid = self.total_clean

        # Success rate
        self.success_rate = (
            round((self.employees_created / self.total_original * 100), 2)
            if self.total_original > 0
            else 0
        )

        # Cleaning statistics
        self.cleaning_stats.setdefault(
            "emails_cleaned",
            len(self.df_clean) if "email" in self.df_clean.columns else 0,
        )
        self.cleaning_stats.setdefault(
            "phones_cleaned",
            len(self.df_clean) if "phone" in self.df_clean.columns else 0,
        )
        self.cleaning_stats.setdefault(
            "genders_inferred",
            len(self.df_clean) if "gender" in self.df_clean.columns else 0,
        )

        # Date statistics
        self._calculate_date_stats()

        # Relation statistics
        self._set_relation_defaults()

    def _calculate_date_stats(self):
        """Calculates statistics related to dates.

        Args: None
        Returns: None
        """

        if (
            "birthdate" in self.df_clean.columns
            and "hire_date" in self.df_clean.columns
        ):
            df_temp = self.df_clean.copy()
            df_temp["birthdate"] = pd.to_datetime(df_temp["birthdate"], errors="coerce")
            df_temp["hire_date"] = pd.to_datetime(df_temp["hire_date"], errors="coerce")

            age_at_hire = (df_temp["hire_date"] - df_temp["birthdate"]).dt.days // 365
            self.cleaning_stats.setdefault(
                "underage_hires", int((age_at_hire < 18).sum())
            )
            self.cleaning_stats.setdefault(
                "adult_hires", int((age_at_hire >= 18).sum())
            )

            if "termination_date" in df_temp.columns:
                df_temp["termination_date"] = pd.to_datetime(
                    df_temp["termination_date"], errors="coerce"
                )
                term_before_hire = df_temp["termination_date"] < df_temp["hire_date"]
                self.cleaning_stats.setdefault(
                    "terminated_before_hire", int(term_before_hire.sum())
                )

    def _set_relation_defaults(self):
        """Sets default values for relation statistics."""
        self.relation_stats.setdefault("employees_without_sales", 0)
        self.relation_stats.setdefault("employees_with_sales", len(self.df_clean))
        self.relation_stats.setdefault("invalid_employee_ids_in_sales", 0)
        self.relation_stats.setdefault("invalid_names_in_sales", 0)

    def generate(self) -> Dict[str, Any]:
        """
        Generates the employee report data.

        Returns:
            Dict with all necessary data for the report.
        """
        return {
            "report_type": "employees",
            "title": "EMPLOYEE DATASET ANALYSIS REPORT",
            "total_original": self.total_original,
            "total_clean": self.total_clean,
            "total_valid": self.total_valid,
            "employees_created": self.employees_created,
            "success_rate": self.success_rate,
            "cleaning_stats": self.cleaning_stats,
            "relation_stats": self.relation_stats,
            "df_original": self.df_original,
            "df_clean": self.df_clean,
            "validations": self.validations,
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns an executive summary of the report."""
        return {
            "total_analyzed": self.total_original,
            "after_cleaning": self.total_clean,
            "valid_records": self.total_valid,
            "instances_created": self.employees_created,
            "success_rate": self.success_rate,
        }

    def get_cleaning_metrics(self) -> Dict[str, Any]:
        """Returns cleaning metrics."""
        return {
            "retention_rate": round((self.total_clean / self.total_original * 100), 2)
            if self.total_original > 0
            else 0,
            "validation_rate": round((self.total_valid / self.total_clean * 100), 2)
            if self.total_clean > 0
            else 0,
            "overall_success": self.success_rate,
        }


def create_employees_report(
    df_employees: pd.DataFrame,
    df_employees_clean: pd.DataFrame,
    validations: pd.DataFrame,
    employees_created: int,
        cleaning_stats: Optional[Dict[str, Any]] = None,
        relation_stats: Optional[Dict[str, Any]] = None,) -> EmployeesReport:
    """
    Factory function to create an employees report.

    Args:
        df_employees: Original employees DataFrame
        df_employees_clean: Clean employees DataFrame
        validations: DataFrame with validation results
        employees_created: NNumber of Employee instances created
        cleaning_stats: Optional cleaning statistics
        relation_stats: Optional relation statistics

    Returns:
        EmployeesReport with all calculated data
    """
    return EmployeesReport(
        df_original=df_employees,
        df_clean=df_employees_clean,
        validations=validations,
        employees_created=employees_created,
        cleaning_stats=cleaning_stats,
        relation_stats=relation_stats,
    )
