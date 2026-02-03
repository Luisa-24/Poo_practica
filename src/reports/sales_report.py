"""
Module for generating sales reports.
This module has been simplified - PDF generation is done
through create_graphs.py and fill_template.py using LaTeX.
"""
# ESTANDAR
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import pandas as pd

# LOCALES
from .report import Report


@dataclass
class SalesReport(Report):
    """Class to manage sales report data."""

    df_original: pd.DataFrame
    df_clean: pd.DataFrame
    validations: pd.DataFrame
    sales_created: int
    cleaning_stats: Optional[Dict[str, Any]] = field(default_factory=dict)
    relation_stats: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        if self.cleaning_stats is None:
            self.cleaning_stats = {}
        if self.relation_stats is None:
            self.relation_stats = {}
        self._calculate_stats()

    def _calculate_stats(self):
        """Calculates statistics for the sales dataset."""
        # Basic statistics
        self.total_original = len(self.df_original)
        self.total_clean = len(self.df_clean)

        # Total valid = total clean (successfully processed records)
        self.total_valid = self.total_clean

        # Success rate
        self.success_rate = round(
            (self.sales_created / self.total_original * 100), 2
        ) if self.total_original > 0 else 0

        # Calculate total revenue
        self._calculate_revenue_stats()

        # Date statistics
        self._calculate_date_stats()

        # Status statistics
        self._calculate_status_stats()

        # Relation statistics
        self._set_relation_defaults()

    def _calculate_revenue_stats(self):
        """Calculates revenue statistics."""
        price_col = 'total_price' if 'total_price' in self.df_clean.columns else 'Total Price'
        if price_col in self.df_clean.columns:
            self.total_revenue = float(self.df_clean[price_col].sum())
            self.avg_sale = float(self.df_clean[price_col].mean())
            self.max_sale = float(self.df_clean[price_col].max())
            self.min_sale = float(self.df_clean[price_col].min())
        else:
            self.total_revenue = 0
            self.avg_sale = 0
            self.max_sale = 0
            self.min_sale = 0

        qty_col = 'quantity' if 'quantity' in self.df_clean.columns else 'Quantity'
        if qty_col in self.df_clean.columns:
            self.total_quantity = int(self.df_clean[qty_col].sum())
            self.avg_quantity = float(self.df_clean[qty_col].mean())
        else:
            self.total_quantity = 0
            self.avg_quantity = 0

    def _calculate_date_stats(self):
        """Calculates date-related statistics."""
        date_col = 'sale_date' if 'sale_date' in self.df_original.columns else 'Sale Date'
        if date_col in self.df_original.columns:
            df_temp = self.df_original.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            current_date = pd.Timestamp.now()

            future_dates = (df_temp[date_col] > current_date).sum()
            self.cleaning_stats.setdefault('future_dates', int(future_dates))
            self.cleaning_stats.setdefault(
                'future_dates_pct',
                round(future_dates / len(self.df_original) * 100, 2) if len(self.df_original) > 0 else 0
            )

        self.cleaning_stats.setdefault('sales_before_hire', 0)
        self.cleaning_stats.setdefault('sales_reassigned', 0)
        self.cleaning_stats.setdefault('dates_corrected', 0)

    def _calculate_status_stats(self):
        """Calculates sales status statistics."""
        status_col = 'sale_status' if 'sale_status' in self.df_original.columns else 'Sale Status'
        date_col = 'sale_date' if 'sale_date' in self.df_original.columns else 'Sale Date'

        if status_col in self.df_original.columns:
            self.status_distribution = self.df_original[status_col].value_counts().to_dict()

            # Old pending sales (> 5 years)
            if date_col in self.df_original.columns:
                df_temp = self.df_original.copy()
                df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                pending = df_temp[df_temp[status_col] == 'Pending']
                five_years_ago = pd.Timestamp.now() - pd.DateOffset(years=5)
                old_pending = (pending[date_col] < five_years_ago).sum()
                self.cleaning_stats.setdefault('old_pending_sales', int(old_pending))
        else:
            self.status_distribution = {}

    def _set_relation_defaults(self):
        """Sets default values for relation statistics."""
        self.relation_stats.setdefault('sales_with_valid_employee', len(self.df_clean))
        self.relation_stats.setdefault('sales_with_invalid_employee', 0)
        self.relation_stats.setdefault('sales_before_hire', 0)

    def generate(self) -> Dict[str, Any]:
        """
        Generates the sales report data.

        Returns:
            Dict with all necessary data for the report.
        """
        return {
            'report_type': 'sales',
            'title': 'SALES DATASET ANALYSIS REPORT',
            'total_original': self.total_original,
            'total_clean': self.total_clean,
            'total_valid': self.total_valid,
            'sales_created': self.sales_created,
            'success_rate': self.success_rate,
            'total_revenue': self.total_revenue,
            'avg_sale': self.avg_sale,
            'max_sale': self.max_sale,
            'min_sale': self.min_sale,
            'total_quantity': self.total_quantity,
            'avg_quantity': self.avg_quantity,
            'status_distribution': self.status_distribution,
            'cleaning_stats': self.cleaning_stats,
            'relation_stats': self.relation_stats,
            'df_original': self.df_original,
            'df_clean': self.df_clean,
            'validations': self.validations
        }

    def get_summary(self) -> Dict[str, Any]:
        """Returns a summary of the report."""
        return {
            'total_analyzed': self.total_original,
            'after_cleaning': self.total_clean,
            'valid_records': self.total_valid,
            'instances_created': self.sales_created,
            'success_rate': self.success_rate,
            'total_revenue': self.total_revenue
        }

    def get_financial_metrics(self) -> Dict[str, Any]:
        """Returns financial metrics."""
        return {
            'total_revenue': self.total_revenue,
            'average_sale': self.avg_sale,
            'max_sale': self.max_sale,
            'min_sale': self.min_sale,
            'total_units_sold': self.total_quantity,
            'avg_units_per_sale': self.avg_quantity
        }

    def get_cleaning_metrics(self) -> Dict[str, Any]:
        """Returns cleaning metrics."""
        return {
            'retention_rate': round(
                (self.total_clean / self.total_original * 100), 2
            ) if self.total_original > 0 else 0,
            'validation_rate': round(
                (self.total_valid / self.total_clean * 100), 2
            ) if self.total_clean > 0 else 0,
            'overall_success': self.success_rate
        }


def create_sales_report(
    df_sales: pd.DataFrame,
    df_sales_clean: pd.DataFrame,
    validations: pd.DataFrame,
    sales_created: int,
    cleaning_stats: Optional[Dict[str, Any]] = None,
    relation_stats: Optional[Dict[str, Any]] = None) -> SalesReport:
    """
    Factory function for creating a sales report.

    Args:
        df_sales: Original sales DataFrame
        df_sales_clean: Clean sales DataFrame
        validations: DataFrame with validation results
        sales_created: Number of sale instances created
        cleaning_stats: Optional cleaning statistics
        relation_stats: Optional relation statistics

    Returns:
        SalesReport with all calculated data
    """
    return SalesReport(
        df_original=df_sales,
        df_clean=df_sales_clean,
        validations=validations,
        sales_created=sales_created,
        cleaning_stats=cleaning_stats,
        relation_stats=relation_stats
    )
