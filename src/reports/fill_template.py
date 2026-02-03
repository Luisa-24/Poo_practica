# ESTANDAR
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd


# LOCALES
from .create_graphs import generate_report_graphs


class LaTeXTemplateProcessor:
    """Processor for LaTeX report templates."""

    def __init__(
        self,
        template_path: str | None = None,
        output_dir: str = "src/reports/output",
        report_type: str = "employees",
    ):
        """
        Initializes the template processor.

        Args:
            template_path: Path to the LaTeX template
            output_dir: Output directory for generated files
            report_type: 'employees' or 'sales'
        """
        if template_path is None:
            # Use the default template
            template_path = os.path.join(
                os.path.dirname(__file__), "templates", "report_template.tex"
            )

        self.template_path = Path(template_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_type = report_type

        # Create directory for graphs
        self.graphs_dir = self.output_dir / "graphs"
        self.graphs_dir.mkdir(parents=True, exist_ok=True)

        # Read template
        with open(self.template_path, "r", encoding="utf-8") as f:
            self.template_content = f.read()

    def _escape_latex(self, text: str) -> str:
        """Escapes special LaTeX characters."""
        if not isinstance(text, str):
            text = str(text)

        # Characters that need escaping in LaTeX
        special_chars = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }

        for char, escaped in special_chars.items():
            text = text.replace(char, escaped)

        return text

    def _format_number(self, value: float, decimals: int = 2) -> str:
        """Formats a number with thousand separators."""
        if isinstance(value, (int, float)):
            if decimals == 0 or value == int(value):
                return f"{int(value):,}".replace(",", "{,}")
            return f"{value:,.{decimals}f}".replace(",", "{,}")
        return str(value)

    def _format_currency(self, value: float) -> str:
        """Formats a value as currency."""
        return f"\\${self._format_number(value)}"

    def _generate_table_rows(
        self, data: List[Dict[str, Any]], columns: List[str]
    ) -> str:
        """Generates LaTeX table rows."""
        rows = []
        for item in data:
            row_values = [self._escape_latex(str(item.get(col, ""))) for col in columns]
            rows.append(" & ".join(row_values) + " \\\\")
        return "\n        ".join(rows)

    def _create_missing_values_content(self, df: pd.DataFrame) -> str:
        """Generates missing values content."""
        null_counts = df.isnull().sum()
        null_pct = (df.isnull().mean() * 100).round(2)

        cols_with_nulls = null_counts[null_counts > 0]

        if len(cols_with_nulls) == 0:
            return "No missing values found in the dataset."

        content = """
\\begin{table}[H]
    \\centering
    \\caption{Missing Values by Column}
    \\begin{tabular}{lcc}
        \\toprule
        \\textbf{Column} & \\textbf{Missing} & \\textbf{Percentage}\\\\
        \\midrule
"""
        for col in cols_with_nulls.head(10).index:
            col_escaped = self._escape_latex(col[:25])
            content += f"        {col_escaped} & {int(null_counts[col])} & {null_pct[col]:.2f}\\%\\\\\n"

        content += """\\bottomrule
    \\end{tabular}
\\end{table}
"""
        return content

    def _create_validation_results_table(self, validations: pd.DataFrame) -> str:
        """Generates validation results table."""
        if len(validations) == 0:
            return "No validation results available."

        content = """
\\begin{table}[H]
    \\centering
    \\caption{Validation Results by Rule}
    \\begin{tabular}{lcccc}
        \\toprule
        \\textbf{Validation} & \\textbf{VValid} & \\textbf{Invalid} & \\textbf{N/A} &
        \\textbf{\\% Success}\\\\
        \\midrule
"""
        for col in validations.columns:
            if col not in ["employee_id", "sale_id", "product_id", "name"]:
                true_count = int(validations[col].astype(bool).sum())
                false_count = int((~validations[col].astype(bool)).sum())
                none_count = int(validations[col].isna().sum())
                total = true_count + false_count
                pct = round(true_count / total * 100, 1) if total > 0 else 100
                col_escaped = self._escape_latex(col[:22])
                content += (
                    f"        {col_escaped} & {true_count} & {false_count} & "
                    f"{none_count} & {pct}\\%\\\\\n"
                )

        content += """\\bottomrule
    \\end{tabular}
\\end{table}
"""
        return content

    def fill_template(self, report_data: Dict[str, Any], graphs: Dict[str, str]) -> str:
        """
        Fills the template with the report data.

        Args:
            report_data: Dictionary with all report data
            graphs: Dictionary with paths to generated graphs

        Returns:
            Content of the filled LaTeX report.
        """
        content = self.template_content

        # Determinates colors and dataset names based on report type
        if self.report_type == "employees":
            primary_color = "primaryblue"
            dataset_name = "EMPLOYEES DATASET"
        else:
            primary_color = "primaryred"
            dataset_name = "SALES DATASET"

        # Basic variables
        replacements = {
            "VAR_PRIMARY_COLOR": primary_color,
            "VAR_REPORT_TITLE": f"Report of {'Employees' if self.report_type == 'employees' else 'Sales'}",
            "VAR_DATASET_NAME": dataset_name,
            "VAR_GENERATION_DATE": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "VAR_TOTAL_ORIGINAL": self._format_number(
                report_data.get("total_original", 0), 0
            ),
            "VAR_TOTAL_CLEAN": self._format_number(
                report_data.get("total_clean", 0), 0
            ),
            "VAR_TOTAL_VALID": self._format_number(
                report_data.get("total_valid", 0), 0
            ),
            "VAR_SUCCESS_RATE": self._format_number(report_data.get("success_rate", 0)),
        }

        # Instances created
        if self.report_type == "employees":
            replacements["VAR_INSTANCES_CREATED"] = self._format_number(
                report_data.get("employees_created", 0), 0
            )
        else:
            replacements["VAR_INSTANCES_CREATED"] = self._format_number(
                report_data.get("sales_created", 0), 0
            )

        # Metrics calculation
        total_original = report_data.get("total_original", 0)
        total_clean = report_data.get("total_clean", 0)
        total_valid = report_data.get("total_valid", 0)
        instances_created = (
            report_data.get("employees_created", 0)
            if self.report_type == "employees"
            else report_data.get("sales_created", 0)
        )

        retention_rate = (
            round((total_clean / total_original * 100), 2) if total_original > 0 else 0
        )
        validation_rate = (
            round((total_valid / total_clean * 100), 2) if total_clean > 0 else 0
        )

        replacements["VAR_RETENTION_RATE"] = self._format_number(retention_rate)
        replacements["VAR_VALIDATION_RATE"] = self._format_number(validation_rate)
        replacements["VAR_RECORDS_REMOVED"] = self._format_number(
            total_original - total_clean, 0
        )

        # Pipeline changes
        replacements["VAR_CLEAN_CHANGE"] = f"-{total_original - total_clean}"
        replacements["VAR_VALID_CHANGE"] = f"-{total_clean - total_valid}"
        replacements["VAR_INSTANCE_CHANGE"] = f"-{total_valid - instances_created}"

        # Success box style
        success_rate = report_data.get("success_rate", 0)
        if success_rate >= 70:
            replacements["VAR_SUCCESS_BOX_STYLE"] = "successbox"
            conclusion = "\\textbf{EXCELLENT:} The pipeline successfully processed most of the records. \n"
            "The quality of the input data is good."

        elif success_rate >= 50:
            replacements["VAR_SUCCESS_BOX_STYLE"] = "metricbox"
            conclusion = "\\textbf{MODERATE:} Acceptable pipeline performance. \n"
            "It is recommended to review the validations that fail most frequently."
        else:
            replacements["VAR_SUCCESS_BOX_STYLE"] = "alertbox"
            conclusion = "\\textbf{REVIEW:} It is recommended to improve the quality of the input data. \n"
            "Many records do not meet the required validations."

        replacements["VAR_CONCLUSION_CONTENT"] = conclusion
        replacements["VAR_CONCLUSION_BOX_STYLE"] = replacements["VAR_SUCCESS_BOX_STYLE"]

        # Contain dataset specific content
        self._fill_dataset_specific_content(report_data, replacements)

        # Missing values
        df_original = report_data.get("df_original", pd.DataFrame())
        replacements["VAR_MISSING_VALUES_CONTENT"] = (
            self._create_missing_values_content(df_original)
        )
        replacements["VAR_MISSING_VALUES_FIGURE"] = ""

        # Validation results
        validations = report_data.get("validations", pd.DataFrame())
        replacements["VAR_VALIDATION_RESULTS_TABLE"] = (
            self._create_validation_results_table(validations)
        )

        # Chart
        self._fill_graph_references(graphs, replacements)

        # Replace all variables
        for var, value in replacements.items():
            content = content.replace(var, str(value))

        return content

    def _fill_dataset_specific_content(
        self, report_data: Dict[str, Any], replacements: Dict[str, str]
    ):
        """Fill dataset specific content based on the dataset type."""
        if self.report_type == "employees":
            self._fill_employees_content(report_data, replacements)
        else:
            self._fill_sales_content(report_data, replacements)

    def _fill_employees_content(
        self, report_data: Dict[str, Any], replacements: Dict[str, str]
    ):
        """Fill specific content for employees."""
        cleaning_stats = report_data.get("cleaning_stats", {})
        relation_stats = report_data.get("relation_stats", {})

        # Dataset information
        replacements["VAR_DATASET_SPECIFIC_INFO"] = """
The data includes personal, contact, and employment information of employees,
including hire dates, termination dates, department, and salary.
"""

        # Specific analysis (gender)
        replacements["VAR_SPECIFIC_ANALYSIS_TITLE"] = "Gender Consistency Analysis"

        gender_inconsist = cleaning_stats.get("gender_inconsistencies", 0)
        replacements["VAR_SPECIFIC_ANALYSIS_CONTENT"] = f"""
\\subsection{{Gender vs Name Validation}}

The \\texttt{{gender-guesser}} library was used to validate the consistency between
the registered gender and the employee's name.

\\begin{{itemize}}
    \\item Genders validated using name inference
    \\item Employees with inconsistent gender: \\textbf{{{gender_inconsist}}}
    \\item Method: Comparison of registered gender vs inferred from name
\\end{{itemize}}
"""

        # Date validation
        adult_hires = cleaning_stats.get("adult_hires", 0)
        underage_hires = cleaning_stats.get("underage_hires", 0)
        term_before_hire = cleaning_stats.get("terminated_before_hire", 0)

        replacements["VAR_DATE_VALIDATION_CONTENT"] = f"""
\\subsection{{Age at Hiring}}

\\begin{{itemize}}
    \\item Employees hired as adults: \\textbf{{{adult_hires}}}
    \\item Employees hired as minors: \\textbf{{{underage_hires}}}
\\end{{itemize}}

\\subsection{{Termination vs Hiring}}

\\begin{{itemize}}
    \\item Employees terminated before hiring: \\textbf{{{term_before_hire}}}
\\end{{itemize}}
"""

        # Cleaning operations
        replacements["VAR_CLEANING_OPERATIONS"] = """
    \\item Email validation and cleaning (standardized format)
    \\item Phone number cleaning (international format, add 10 zeros to invalid numbers)
    \\item Gender inference based on name (gender-guesser)
    \\item Removal of records without employee\\_id or name
    \\item Removal of Age column (redundant/inconsistent data)
    \\item Conversión de fechas a formato datetime
"""

        # Additional cleaning statistics
        emails_cleaned = cleaning_stats.get("emails_cleaned", 0)
        phones_cleaned = cleaning_stats.get("phones_cleaned", 0)
        genders_inferred = cleaning_stats.get("genders_inferred", 0)

        replacements[
            "VAR_CLEANING_STATS_ROWS"
        ] = f"""        Emails processed & {emails_cleaned}\\\\
        Phones cleaned & {phones_cleaned}\\\\
        Genders inferred & {genders_inferred}\\\\"""

        # Relations
        emp_con_ventas = relation_stats.get("employees_with_sales", 0)
        emp_sin_ventas = relation_stats.get("employees_without_sales", 0)
        ids_invalidos = relation_stats.get("invalid_employee_ids_in_sales", 0)

        replacements["VAR_RELATIONS_CONTENT"] = f"""
\\subsection{{Sales Activity Analysis}}

\\begin{{itemize}}
    \\item Employees with associated sales: \\textbf{{{emp_con_ventas}}}
    \\item Employees without associated sales: \\textbf{{{emp_sin_ventas}}}
\\end{{itemize}}

\\subsection{{Relationship Inconsistencies}}

\\begin{{itemize}}
    \\item Sales with invalid Employee ID: \\textbf{{{ids_invalidos}}}
\\end{{itemize}}
"""

        # Validation rules
        replacements["VAR_VALIDATION_RULES"] = """
    \\item \\textbf{{termination\\_is\\_after\\_hire}}: Termination date major that hire date
        \\item \\textbf{{termination\\_is\\_after\\_birthdate}}: Employee major or iqual 18 years old at \
    termination
    \\item \\textbf{{valid\\_email}}: Email with valid format
    \\item \\textbf{{valid\\_phone}}: Phone with valid format
"""

        # No business metrics section for employees
        replacements["VAR_BUSINESS_METRICS_SECTION"] = ""

    def _fill_sales_content(
        self, report_data: Dict[str, Any], replacements: Dict[str, str]
    ):
        """Fill content specific to sales."""
        cleaning_stats = report_data.get("cleaning_stats", {})
        relation_stats = report_data.get("relation_stats", {})

        total_revenue = report_data.get("total_revenue", 0)

        # Dataset information
        replacements["VAR_DATASET_SPECIFIC_INFO"] = f"""
The data includes information on sales transactions, including products,
quantities, prices, and statuses. The total recorded revenue is
\\textbf{{{self._format_currency(total_revenue)}}}.
"""

        # Specific analysis (statuses)
        replacements["VAR_SPECIFIC_ANALYSIS_TITLE"] = "Sales Status Analysis"

        status_dist = report_data.get("status_distribution", {})
        old_pending = cleaning_stats.get("old_pending_sales", 0)

        status_items = ""
        for status, count in status_dist.items():
            status_items += (
                f"    \\item {self._escape_latex(status)}: \\textbf{{{count}}}\n"
            )

        replacements["VAR_SPECIFIC_ANALYSIS_CONTENT"] = f"""
\\subsection{{Status Distribution}}

\\begin{{itemize}}
{status_items}\\end{{itemize}}

\\subsection{{Old Pending Sales}}

\\begin{{itemize}}
    \\item Sales in Pending status for more than 5 years: \\textbf{{{old_pending}}}
\\end{{itemize}}

{{\\small\\textit{{Note: Sales pending for a long time may indicate issues
in the sales closing process.}}}}
"""

        # Date validation
        future_dates = cleaning_stats.get("future_dates", 0)
        future_pct = cleaning_stats.get("future_dates_pct", 0)
        sales_before_hire = cleaning_stats.get("sales_before_hire", 0)

        replacements["VAR_DATE_VALIDATION_CONTENT"] = f"""
\\subsection{{Future Dates}}
\\begin{{itemize}}
    \\item Sales with future dates: \\textbf{{{future_dates}}} ({future_pct}\\%)
\\end{{itemize}}

\\subsection{{Sales vs Hire Date}}

\\begin{{itemize}}
    \\item Sales made before employee hire date: \\textbf{{{sales_before_hire}}}
\\end{{itemize}}
"""

        # Cleaning operations
        replacements["VAR_CLEANING_OPERATIONS"] = """
    \\item Date validation (sale\\_date > hire\\_date of the seller)
    \\item Reassignment of sales to valid employees when applicable
    \\item Conversion of date columns to datetime
    \\item Verification of seller\\_employee\\_id in employee dataset
    \\item Price consistency validation (unit\\_price * quantity)
"""

        # Additional cleaning statistics
        sales_reassigned = cleaning_stats.get("sales_reassigned", 0)
        dates_corrected = cleaning_stats.get("dates_corrected", 0)

        replacements[
            "VAR_CLEANING_STATS_ROWS"
        ] = f"""  Sales reassigned & {sales_reassigned}\\\\
        Dates corrected & {dates_corrected}\\\\"""

        # Relaciones
        valid_ids = relation_stats.get("sales_with_valid_employee", 0)
        invalid_ids = relation_stats.get("sales_with_invalid_employee", 0)

        replacements["VAR_RELATIONS_CONTENT"] = f"""
\\subsection{{Employee ID Validation}}

\\begin{{itemize}}
    \\item Sales with valid Employee ID: \\textbf{{{valid_ids}}}
    \\item Sales with invalid Employee ID: \\textbf{{{invalid_ids}}}
\\end{{itemize}}

\\subsection{{Referential Integrity}}

It was verified that each sale has a valid seller registered in the employee dataset.
Sales with invalid IDs may indicate records of deleted employees or data entry errors.
"""

        # Validation rules
        replacements["VAR_VALIDATION_RULES"] = """
    \\item \\textbf{{is\\_pending}}: Status = 'Pending'
    \\item \\textbf{{is\\_completed}}: Status = 'Completed'
    \\item \\textbf{{is\\_cancelled}}: Status = 'Cancelled'
    \\item \\textbf{{is\\_future\\_date}}: Sale date is not in the future
    \\item \\textbf{{validate\\_prices}}: Prices are positive
    \\item \\textbf{{validate\\_total\\_price}}: total\\_price = quantity * unit\\_price
"""

        # Section of business metrics
        replacements["VAR_BUSINESS_METRICS_SECTION"] = ""

    def _fill_graph_references(
        self, graphs: Dict[str, str], replacements: Dict[str, str]
    ):
        """Adds references to the graphs in the variables."""

        # Convert paths to relative for LaTeX
        def make_relative(path):
            if path:
                return os.path.basename(path)
            return ""

        # Pipeline graph
        if "pipeline_flow" in graphs:
            replacements["VAR_PIPELINE_FLOW_GRAPH"] = make_relative(
                graphs["pipeline_flow"]
            )
        else:
            replacements["VAR_PIPELINE_FLOW_GRAPH"] = "pipeline_flow.png"

        # Specific analysis figures
        specific_figures = ""
        if self.report_type == "employees":
            if "gender_distribution" in graphs:
                specific_figures += f"""
\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.6\\textwidth]{{graphs/{make_relative(graphs["gender_distribution"])}}}
    \\caption{{Gender Distribution}}
\\end{{figure}}
"""
            if "department_distribution" in graphs:
                specific_figures += f"""
\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{{graphs/{make_relative(graphs["department_distribution"])}}}
    \\caption{{Department Distribution}}
\\end{{figure}}
"""
        else:
            if "status_distribution" in graphs:
                specific_figures += f"""
\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.6\\textwidth]{{graphs/{make_relative(graphs["status_distribution"])}}}
    \\caption{{Sales Status}}
\\end{{figure}}
"""
            if "revenue_by_status" in graphs:
                specific_figures += f"""
\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{{graphs/{make_relative(graphs["revenue_by_status"])}}}
    \\caption{{Revenue by Status}}
\\end{{figure}}
"""

        replacements["VAR_SPECIFIC_ANALYSIS_FIGURES"] = specific_figures

        # Date validation figures
        date_figures = ""
        if "date_validations" in graphs:
            date_figures += f"""
\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{{graphs/{make_relative(graphs["date_validations"])}}}
    \\caption{{Date Validations}}
\\end{{figure}}
"""
        elif "date_issues" in graphs:
            date_figures += f"""
\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{{graphs/{make_relative(graphs["date_issues"])}}}
    \\caption{{Date Issues}}
\\end{{figure}}
"""
        replacements["VAR_DATE_VALIDATION_FIGURES"] = date_figures

        # Relation figures
        relation_figures = ""
        if "employee_activity" in graphs:
            relation_figures += f"""
\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.6\\textwidth]{{graphs/{make_relative(graphs["employee_activity"])}}}
    \\caption{{Employee activity}}
\\end{{figure}}
"""
        if "referential_integrity" in graphs:
            relation_figures += f"""
\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.6\\textwidth]{{graphs/{make_relative(graphs["referential_integrity"])}}}
    \\caption{{Referential Integrity}}
\\end{{figure}}
"""
        replacements["VAR_RELATIONS_FIGURES"] = relation_figures

        # Validation figures
        validation_figures = ""

        if "validation_details" in graphs:
            validation_figures += f"""
\\begin{{figure}}[H]
    \\centering
    \\includegraphics[width=0.9\\textwidth]{{graphs/{make_relative(graphs["validation_details"])}}}
    \\caption{{Validation Details}}
\\end{{figure}}
"""
        replacements["VAR_VALIDATION_FIGURES"] = validation_figures

    def _find_pdflatex(self) -> Optional[str]:
        """Searches for pdflatex in the system."""
        # First try with shutil.which
        pdflatex_cmd = shutil.which("pdflatex")
        if pdflatex_cmd:
            return pdflatex_cmd

        # Search in common Windows locations
        common_paths = [
            # MiKTeX locations
            r"C:\Program Files\MiKTeX\miktex\bin\x64",
            r"C:\Program Files (x86)\MiKTeX\miktex\bin\x64",
            r"C:\Program Files\MiKTeX 2.9\miktex\bin\x64",
            os.path.expanduser(r"~\AppData\Local\Programs\MiKTeX\miktex\bin\x64"),
            os.path.expanduser(r"~\AppData\Local\MiKTeX\miktex\bin\x64"),
            # TeX Live locations
            r"C:\texlive\2024\bin\windows",
            r"C:\texlive\2023\bin\windows",
            r"C:\texlive\2022\bin\windows",
            r"C:\texlive\2025\bin\windows",
            r"C:\texlive\2026\bin\windows",
        ]

        for path in common_paths:
            potential = os.path.join(path, "pdflatex.exe")
            if os.path.exists(potential):
                return potential

        # Search in extended PATH
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for dir_path in path_dirs:
            potential = os.path.join(dir_path, "pdflatex.exe")
            if os.path.exists(potential):
                return potential

        return None

    def _install_miktex(self) -> bool:
        """Attempts to install MiKTeX using winget."""
        print("Attempting to install MiKTeX automatically...")

        try:
            # Check if winget is available
            winget_check = subprocess.run(
                ["winget", "--version"], capture_output=True, text=True, timeout=10
            )

            if winget_check.returncode != 0:
                print("winget is not available.")
                return False

            # Install MiKTeX
            print("Installing MiKTeX with winget (this may take several minutes)...")
            result = subprocess.run(
                [
                    "winget",
                    "install",
                    "--id",
                    "MiKTeX.MiKTeX",
                    "--accept-source-agreements",
                    "--accept-package-agreements",
                ],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes for installation
            )

            if result.returncode == 0:
                print("MiKTeX installed successfully.")
                print(
                    "NOTE: You may need to restart the terminal for pdflatex to be available."
                )
                return True
            else:
                print(f"Error installing MiKTeX: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("Installation timed out.")
            return False
        except FileNotFoundError:
            print("winget not found.")
            return False
        except Exception as e:
            print(f"Error during installation: {e}")
            return False

    def compile_to_pdf(
        self,
            tex_content: str,
            output_filename: str = "report",
            auto_install: bool = False,) -> Optional[str]:

        """
        Compiles the LaTeX content to a PDF file.

        Args:
            tex_content: LaTeX content
            output_filename: Output file name (without extension)
            auto_install: If True, attempts to install MiKTeX automatically

        Returns:
            Path to the generated PDF or None if it fails
        """
        tex_file = self.output_dir / f"{output_filename}.tex"
        pdf_file = self.output_dir / f"{output_filename}.pdf"

        # Save .tex file
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(tex_content)

        # Find pdflatex
        pdflatex_cmd = self._find_pdflatex()

        if pdflatex_cmd is None:
            print("=" * 60)
            print("ERROR: pdflatex not found on the system.")
            print("=" * 60)
            print("\nOptions to resolve:")
            print("\n1. INSTALL MIKTEX (Recommended for Windows):")
            print("   - Download: https://miktex.org/download")
            print("   - Or run: winget install MiKTeX.MiKTeX")
            print("\n2. INSTALL TEX LIVE:")
            print("   - Download: https://www.tug.org/texlive/")
            print("\n3. USE OVERLEAF (Online):")
            print(f"   - Upload the file: {tex_file}")
            print("   - Web: https://www.overleaf.com/")
            print("=" * 60)
            if auto_install:
                if self._install_miktex():
                    # Retry finding after installation
                    pdflatex_cmd = self._find_pdflatex()
            if pdflatex_cmd is None:
                return None

        try:
            # Compile twice to resolve references
            for i in range(2):
                result = subprocess.run(
                    [
                        pdflatex_cmd,
                        "--interaction=nonstopmode",
                        "--enable-installer",
                        tex_file.name,
                    ],
                    capture_output=True,
                    text=True,
                    cwd=str(self.output_dir),
                    timeout=300,
                )

                if result.returncode != 0 and i == 1:
                    # Only show error on the second pass
                    log_file = self.output_dir / f"{output_filename}.log"
                    print(f"Warning: pdflatex finished with code {result.returncode}")
                    if log_file.exists():
                        print(f"See log at: {log_file}")

            if pdf_file.exists():
                # Clean auxiliary files
                for ext in [".aux", ".log", ".out", ".toc"]:
                    aux_file = self.output_dir / f"{output_filename}{ext}"
                    if aux_file.exists():
                        try:
                            aux_file.unlink()
                        except Exception:
                            pass

                return str(pdf_file)
            else:
                log_file = self.output_dir / f"{output_filename}.log"
                print("Error generating PDF.")
                if log_file.exists():
                    # Read last lines of log for diagnosis
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        error_lines = [
                            line
                            for line in lines
                            if "error" in line.lower() or "!" in line
                        ]
                        if error_lines:
                            print("Errors found:")
                            for line in error_lines[:5]:
                                print(f"  {line.strip()}")
                    print(f"Full log at: {log_file}")
                return None

        except subprocess.TimeoutExpired:
            print("Error: LaTeX compilation exceeded time limit.")
            return None
        except Exception as e:
            print(f"Error compiling LaTeX: {e}")
            return None

    def generate_report(
        self, report_data: Dict[str, Any], output_filename: str | None = None
    ) -> Optional[str]:
        """
        Generates the full report (graphs + LaTeX + PDF).

        Args:
            report_data: Dictionary with all report data
            output_filename: Output file name (without extension)

        Returns:
            Path to the generated PDF or None if it fails
        """
        if output_filename is None:
            output_filename = f"report_{self.report_type}"

        # 1. Generate graphs
        graphs = generate_report_graphs(
            report_data, output_dir=str(self.graphs_dir), report_type=self.report_type
        )

        # 2. Fill template
        tex_content = self.fill_template(report_data, graphs)

        # 3. Compile to PDF
        pdf_path = self.compile_to_pdf(tex_content, output_filename)

        return pdf_path


def generate_full_report(
    report_data: Dict[str, Any],
    report_type: str = "employees",
    output_dir: str = "src/reports/output",
    output_filename: str | None = None,
) -> Optional[str]:
    """
    Wrapper function to generate a full report.

    Args:
        report_data: Report data (from EmployeesReport or SalesReport)
        report_type: 'employees' or 'sales'
        output_dir: Output directory
        output_filename: File name (without extension)

    Returns:
        Path to the generated PDF or None if it fails
    """
    processor = LaTeXTemplateProcessor(output_dir=output_dir, report_type=report_type)
    return processor.generate_report(report_data, output_filename)


def generate_employees_pdf(
    df_employees: pd.DataFrame,
    df_employees_clean: pd.DataFrame,
    validations: pd.DataFrame,
    employees_created: int,
    cleaning_stats: Dict[str, Any] | None = None,
    relation_stats: Dict[str, Any] | None = None,
    output_dir: str = "src/reports/output",
) -> Optional[str]:
    """
    Generates the full employees PDF report.

    Args:
        df_employees: Original DataFrame
        df_employees_clean: Clean DataFrame
        validations: Validation results
        employees_created: Number of instances created
        cleaning_stats: Cleaning statistics
        relation_stats: Relation statistics
        output_dir: Output directory

    Returns:
        Path to the generated PDF
    """
    from .employees_report import create_employees_report

    report = create_employees_report(
        df_employees,
        df_employees_clean,
        validations,
        employees_created,
        cleaning_stats,
        relation_stats,
    )

    report_data = report.generate()

    return generate_full_report(
        report_data,
        report_type="employees",
        output_dir=output_dir,
        output_filename="report_employees_en",
    )


def generate_sales_pdf(
    df_sales: pd.DataFrame,
    df_sales_clean: pd.DataFrame,
    validations: pd.DataFrame,
    sales_created: int,
    cleaning_stats: Dict[str, Any] | None = None,
    relation_stats: Dict[str, Any] | None = None,
    output_dir: str = "src/reports/output",
) -> Optional[str]:
    """
    Generates the full sales PDF report.

    Args:
        df_sales: Original DataFrame
        df_sales_clean: Clean DataFrame
        validations: Validation results
        sales_created: Number of instances created
        cleaning_stats: Cleaning statistics
        relation_stats: Relation statistics
        output_dir: Output directory

    Returns:
        Path to the generated PDF
    """
    from .sales_report import create_sales_report

    report = create_sales_report(
        df_sales,
        df_sales_clean,
        validations,
        sales_created,
        cleaning_stats,
        relation_stats,
    )

    report_data = report.generate()

    return generate_full_report(
        report_data,
        report_type="sales",
        output_dir=output_dir,
        output_filename="report_sales_en",
    )
