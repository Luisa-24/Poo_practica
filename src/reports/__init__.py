"""
Módulo de reportes para el proyecto POO.
Genera reportes de análisis de datos de empleados y ventas usando LaTeX.
"""

from .report import Report
from .employees_report import EmployeesReport, create_employees_report
from .sales_report import SalesReport, create_sales_report
from .create_graphs import (
    ReportGraphGenerator,
    generate_report_graphs
)
from .fill_template import (
    LaTeXTemplateProcessor,
    generate_full_report,
    generate_employees_pdf,
    generate_sales_pdf
)

__all__ = [
    "Report",
    "EmployeesReport",
    "create_employees_report",
    "SalesReport",
    "create_sales_report",
    "ReportGraphGenerator",
    "generate_report_graphs",
    "LaTeXTemplateProcessor",
    "generate_full_report",
    "generate_employees_pdf",
    "generate_sales_pdf",
]
