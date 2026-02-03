# ESTANDAR
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns  # type: ignore
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Union, cast
from pathlib import Path
matplotlib.use("Agg")  # Backend without GUI for image generation


# Global configurations for plots
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 10


class ReportGraphGenerator:
    """Graph generator for reports."""

    # Color palettes
    EMPLOYEES_PALETTE = ["#1a5276", "#2980b9", "#3498db", "#5dade2", "#85c1e9"]
    SALES_PALETTE = ["#7b241c", "#c0392b", "#e74c3c", "#ec7063", "#f1948a"]
    SUCCESS_COLORS = {"success": "#27ae60", "warning": "#f39c12", "danger": "#e74c3c"}
    GENERAL_PALETTE = ["#3498db", "#27ae60", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c"]

    def __init__(self, output_dir: str, report_type: str = "employees"):
        """
        Initializes the graph generator.

        Args:
            output_dir: Directory where graphs will be saved
            report_type: 'employees' or 'sales' to determine color palette
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_type = report_type
        self.palette = (
            self.EMPLOYEES_PALETTE if report_type == "employees" else self.SALES_PALETTE
        )
        self.generated_graphs: List[str] = []

    def _save_figure(self, fig: plt.Figure, filename: str, dpi: int = 150) -> str:
        """Saves a figure and returns the path."""
        filepath = self.output_dir / filename
        fig.savefig(
            filepath, dpi=dpi, bbox_inches="tight", facecolor="white", edgecolor="none"
        )
        plt.close(fig)
        self.generated_graphs.append(str(filepath))
        return str(filepath)

    # =========================================================================
    # BAR CHARTS
    # =========================================================================

    def create_bar_chart(
        self,
            data: Dict[str, Union[int, float]],
            title: str,
            xlabel: str = "",
            ylabel: str = "",
            filename: str = "bar_chart.png",
            horizontal: bool = False,
            show_values: bool = True,
            figsize: Tuple[int, int] = (10, 6),) -> str:

        """
        Create a bar chart.

        Args:
            data: Dictionary with labels and values
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            filename: Output file name
            horizontal: If True, horizontal bars
            show_values: If True, shows values on bars
            figsize: Figure size

        Returns:
            Path to the generated file
        """
        fig, ax = plt.subplots(figsize=figsize)

        labels = list(data.keys())
        values = list(data.values())
        colors = self.palette[: len(values)]

        if horizontal:
            bars = ax.barh(labels, values, color=colors)
            if show_values:
                for bar, val in zip(bars, values):
                    ax.text(
                        val + max(values) * 0.01,
                        bar.get_y() + bar.get_height() / 2,
                        f"{val:,.0f}",
                        va="center",
                        fontsize=9,
                    )
        else:
            bars = ax.bar(labels, values, color=colors)
            if show_values:
                for bar, val in zip(bars, values):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height(),
                        f"{val:,.0f}",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                    )
            plt.xticks(rotation=45, ha="right")

        ax.set_title(title, fontweight="bold", pad=15)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self._save_figure(fig, filename)

    def create_grouped_bar_chart(
            self,
            data: pd.DataFrame,
            x_col: str,
            y_cols: List[str],
            title: str,
            xlabel: str = "",
            ylabel: str = "",
            filename: str = "grouped_bar.png",
            figsize: Tuple[int, int] = (12, 6),) -> str:
        """Create a grouped bar chart."""
        fig, ax = plt.subplots(figsize=figsize)

        x = np.arange(len(data[x_col]))
        width = 0.8 / len(y_cols)

        for i, col in enumerate(y_cols):
            offset = (i - len(y_cols) / 2 + 0.5) * width
            ax.bar(
                x + offset, data[col], width, label=col, color=self.GENERAL_PALETTE[i]
            )

        ax.set_title(title, fontweight="bold", pad=15)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_xticks(x)
        ax.set_xticklabels(data[x_col], rotation=45, ha="right")
        ax.legend()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self._save_figure(fig, filename)

    # =========================================================================
    # PIE CHARTS
    # =========================================================================

    def create_pie_chart(
        self,
            data: Dict[str, Union[int, float]],
            title: str,
            filename: str = "pie_chart.png",
            show_percentages: bool = True,
            explode_max: bool = False,
            figsize: Tuple[int, int] = (8, 8),) -> str:
        """
        Create a pie chart.

        Args:
            data: Dictionary with labels and values
            title: Chart title
            filename: Output file name
            show_percentages: If True, shows percentages
            explode_max: If True, highlights the largest category
            figsize: Figure size

        Returns:
            Path to the generated file
        """
        fig, ax = plt.subplots(figsize=figsize)

        labels = list(data.keys())
        values = list(data.values())
        colors = self.GENERAL_PALETTE[: len(values)]

        if sum(values) == 0:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=14)
            ax.set_title(title, fontweight="bold")
            return self._save_figure(fig, filename)

        explode = None
        if explode_max and values:
            max_idx = values.index(max(values))
            explode = [0.05 if i == max_idx else 0 for i in range(len(values))]

        autopct = "%1.1f%%" if show_percentages else None

        pie_result = ax.pie(
            values,
            labels=labels,
            autopct=autopct,
            colors=colors,
            explode=explode,
            startangle=90,
            shadow=False,
        )
    
        if len(pie_result) == 3:
            wedges, texts, autotexts = pie_result  # type: ignore
        else:
            wedges, texts = pie_result  # type: ignore
            autotexts = []

        if show_percentages and autotexts:
            for autotext in autotexts:
                autotext.set_fontsize(9)
                autotext.set_fontweight("bold")

        ax.set_title(title, fontweight="bold", pad=15)

        plt.tight_layout()
        return self._save_figure(fig, filename)

    def create_donut_chart(
        self,
            data: Dict[str, Union[int, float]],
            title: str,
            center_text: str = "",
            filename: str = "donut_chart.png",
            figsize: Tuple[int, int] = (8, 8),) -> str:

        """Create a donut chart."""
        fig, ax = plt.subplots(figsize=figsize)

        labels = list(data.keys())
        values = list(data.values())
        colors = self.GENERAL_PALETTE[: len(values)]

        wedges, texts, autotexts = ax.pie(  # type: ignore
            values,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            pctdistance=0.75,
        )

        # Create the center hole
        centre_circle = plt.Circle((0, 0), 0.50, fc="white")
        ax.add_artist(centre_circle)

        if center_text:
            ax.text(
                0,
                0,
                center_text,
                ha="center",
                va="center",
                fontsize=14,
                fontweight="bold",
            )

        ax.set_title(title, fontweight="bold", pad=15)

        plt.tight_layout()
        return self._save_figure(fig, filename)

    # =========================================================================
    # LINE CHARTS
    # =========================================================================

    def create_line_chart(
        self,
            data: pd.DataFrame,
            x_col: str,
            y_col: str,
            title: str,
            xlabel: str = "",
            ylabel: str = "",
            filename: str = "line_chart.png",
            marker: str = "o",
            figsize: Tuple[int, int] = (12, 6),) -> str:

        """Create a line chart."""
        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(
            data[x_col],
            data[y_col],
            marker=marker,
            color=self.palette[0],
            linewidth=2,
            markersize=6,
        )

        ax.set_title(title, fontweight="bold", pad=15)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        return self._save_figure(fig, filename)

    # =========================================================================
    # DISTRIBUTION CHARTS
    # =========================================================================

    def create_histogram(
        self,
            data: pd.Series,
            title: str,
            xlabel: str = "",
            ylabel: str = "Frecuencia",
            bins: int = 30,
            filename: str = "histogram.png",
            show_kde: bool = True,
            figsize: Tuple[int, int] = (10, 6),) -> str:

        """Create a histogram with optional KDE."""
        fig, ax = plt.subplots(figsize=figsize)

        sns.histplot(data, bins=bins, kde=show_kde, color=self.palette[0], ax=ax)

        ax.set_title(title, fontweight="bold", pad=15)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self._save_figure(fig, filename)

    def create_boxplot(
        self,
            data: pd.DataFrame,
            columns: List[str],
            title: str,
            xlabel: str = "",
            ylabel: str = "",
            filename: str = "boxplot.png",
            figsize: Tuple[int, int] = (10, 6),) -> str:

        """Create a boxplot."""
        fig, ax = plt.subplots(figsize=figsize)

        data_to_plot = data[columns]
        bp = ax.boxplot(  # type: ignore
            [data_to_plot[col].dropna() for col in columns],
            tick_labels=columns,
            patch_artist=True,
        )

        for patch, color in zip(bp["boxes"], self.GENERAL_PALETTE):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_title(title, fontweight="bold", pad=15)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        return self._save_figure(fig, filename)

    # =========================================================================
    # HEATMAPS
    # =========================================================================

    def create_heatmap(
        self,
            data: pd.DataFrame,
            title: str,
            filename: str = "heatmap.png",
            annot: bool = True,
            cmap: str = "Blues",
            figsize: Tuple[int, int] = (10, 8),) -> str:

        """Create a heatmap."""
        fig, ax = plt.subplots(figsize=figsize)

        sns.heatmap(data, annot=annot, cmap=cmap, ax=ax, fmt=".2f", linewidths=0.5)

        ax.set_title(title, fontweight="bold", pad=15)

        plt.tight_layout()
        return self._save_figure(fig, filename)

    # =========================================================================
    # FLOW/PROCESS CHARTS
    # =========================================================================

    def create_pipeline_flow_chart(
        self,
            stages: List[str],
            values: List[int],
            title: str = "Pipeline Flow",
            filename: str = "pipeline_flow.png",
            figsize: Tuple[int, int] = (14, 6),) -> str:
        """
        Create a pipeline flow chart.

        Args:
            stages: List of stage names
            values: List of values for each stage
            title: Chart title
            filename: Output file name
            figsize: Figure size

        Returns:
            Path to the generated file
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Gradient colors
        colors = plt.colormaps["Blues"](np.linspace(0.3, 0.9, len(stages)))  # type: ignore

        bars = ax.bar(stages, values, color=colors, edgecolor="white", linewidth=2)

        # Add values and arrows
        for i, (bar, val) in enumerate(zip(bars, values)):
            # Value above the bar
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(values) * 0.02,
                f"{val:,}",
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold",
            )

            # Arrow to the next
            if i < len(bars) - 1:
                ax.annotate(
                    "",
                    xy=(i + 0.8, values[i + 1] + max(values) * 0.1),
                    xytext=(i + 0.2, values[i] + max(values) * 0.1),
                    arrowprops=dict(arrowstyle="->", color="gray", lw=2),
                )

                # Difference
                diff = values[i + 1] - values[i]
                color = (
                    self.SUCCESS_COLORS["success"]
                    if diff >= 0
                    else self.SUCCESS_COLORS["danger"]
                )
                ax.text(
                    i + 0.5,
                    max(values[i], values[i + 1]) + max(values) * 0.15,
                    f"{diff:+,}",
                    ha="center",
                    fontsize=9,
                    color=color,
                    fontweight="bold",
                )

        ax.set_title(title, fontweight="bold", pad=20, fontsize=14)
        ax.set_ylabel("Records", fontsize=11)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_ylim(0, max(values) * 1.3)

        plt.xticks(fontsize=10)
        plt.tight_layout()
        return self._save_figure(fig, filename)

    # =========================================================================
    # VALIDATION CHARTS
    # =========================================================================

    def create_validation_chart(
        self,
            validations: Dict[str, Tuple[int, int]],
            title: str = "Validation Results",
            filename: str = "validation_results.png",
            figsize: Tuple[int, int] = (12, 6),) -> str:
        """
        Create a validation results chart.

        Args:
            validations: Dict with {validation_name: (valid, invalid)}
            title: Chart title
            filename: Output file name
            figsize: Figure size

        Returns:
            Path to the generated file
        """
        fig, ax = plt.subplots(figsize=figsize)

        labels = list(validations.keys())
        valid_counts = [v[0] for v in validations.values()]
        invalid_counts = [v[1] for v in validations.values()]

        x = np.arange(len(labels))
        width = 0.35

        bars1 = ax.bar(
            x - width / 2,
            valid_counts,
            width,
            label="Valid",
            color=self.SUCCESS_COLORS["success"],
            alpha=0.8,
        )
        bars2 = ax.bar(
            x + width / 2,
            invalid_counts,
            width,
            label="Invalid",
            color=self.SUCCESS_COLORS["danger"],
            alpha=0.8,
        )

        # Add values
        for bar in bars1:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        for bar in bars2:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{int(height)}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        ax.set_title(title, fontweight="bold", pad=15)
        ax.set_ylabel("Count")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.legend()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self._save_figure(fig, filename)

    # =========================================================================
    # Specific charts for employees
    # =========================================================================

    def create_gender_distribution(
        self,
        df: pd.DataFrame,
        gender_col: str = "gender",
        filename: str = "gender_distribution.png",
    ) -> str:
        """Create gender distribution chart."""
        if gender_col not in df.columns:
            gender_col = "Gender"

        if gender_col in df.columns:
            gender_counts = cast(Dict[str, Union[int, float]], {str(k): v for k, v in df[gender_col].value_counts().to_dict().items()})
            return self.create_pie_chart(
                gender_counts, "Gender Distribution", filename, explode_max=True
            )
        return ""

    def create_department_distribution(
        self,
            df: pd.DataFrame,
            dept_col: str = "department",
            filename: str = "department_distribution.png",) -> str:

        """Create department distribution chart."""
        if dept_col not in df.columns:
            dept_col = "Department"

        if dept_col in df.columns:
            dept_counts = cast(Dict[str, Union[int, float]], {str(k): v for k, v in df[dept_col].value_counts().to_dict().items()})
            return self.create_bar_chart(
                dept_counts,
                "Department Distribution",
                ylabel="Number of Employees",
                filename=filename,
                horizontal=True,
            )
        return ""

    def create_age_distribution(
        self,
            df: pd.DataFrame,
            age_col: str = "age",
            filename: str = "age_distribution.png",) -> str:

        """Create age distribution histogram."""
        if age_col not in df.columns:
            age_col = "Age"

        if age_col in df.columns:
            ages = df[age_col].dropna()
            # Filter valid ages
            ages = ages[(ages >= 0) & (ages <= 120)]
            return self.create_histogram(
                ages, "Age Distribution", xlabel="Age", filename=filename
            )
        return ""

    # =========================================================================
    # Sales-specific charts
    # =========================================================================

    def create_status_distribution(
        self,
            df: pd.DataFrame,
            status_col: str = "sale_status",
            filename: str = "status_distribution.png",) -> str:

        """Create sale status distribution chart."""
        if status_col not in df.columns:
            status_col = "Sale Status"

        if status_col in df.columns:
            status_counts = cast(Dict[str, Union[int, float]], {str(k): v for k, v in df[status_col].value_counts().to_dict().items()})
            return self.create_donut_chart(
                status_counts,
                "Sale Statuses",
                center_text=f"{len(df)}\nSales",
                filename=filename,
            )
        return ""

    def create_revenue_by_status(
        self,
            df: pd.DataFrame,
            status_col: str = "sale_status",
            price_col: str = "total_price",
            filename: str = "revenue_by_status.png",) -> str:

        """Create revenue by sale status chart."""
        if status_col not in df.columns:
            status_col = "Sale Status"
        if price_col not in df.columns:
            price_col = "Total Price"

        if status_col in df.columns and price_col in df.columns:
            revenue_by_status = df.groupby(status_col)[price_col].sum().to_dict()
            return self.create_bar_chart(
                revenue_by_status,
                "Revenue by Sale Status",
                ylabel="Revenue ($)",
                filename=filename,
            )
        return ""

    def create_quantity_distribution(
        self,
            df: pd.DataFrame,
            qty_col: str = "quantity",
            filename: str = "quantity_distribution.png",) -> str:

        """Create quantity distribution histogram."""
        if qty_col not in df.columns:
            qty_col = "Quantity"

        if qty_col in df.columns:
            return self.create_histogram(
                df[qty_col].dropna(),
                "Quantity Distribution",
                xlabel="Quantity",
                filename=filename,
                bins=20,
            )
        return ""

    def create_price_distribution(
        self,
            df: pd.DataFrame,
            price_col: str = "total_price",
            filename: str = "price_distribution.png",) -> str:

        """Crea histograma de distribución de precios."""
        if price_col not in df.columns:
            price_col = "Total Price"

        if price_col in df.columns:
            return self.create_histogram(
                df[price_col].dropna(),
                "Distribución de Precios Totales",
                xlabel="Precio Total ($)",
                filename=filename,
                bins=30,
            )
        return ""

    # =========================================================================
    # COMPLETE GENERATOR
    # =========================================================================

    def generate_all_graphs(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all graphs for the report.

        Args:
            report_data: Dictionary with all report data

        Returns:
            Dictionary with {chart_name: file_path}
        """
        graphs = {}

        df_original = report_data.get("df_original", pd.DataFrame())
        df_clean = report_data.get("df_clean", pd.DataFrame())
        validations = report_data.get("validations", pd.DataFrame())

        # Pipeline flow chart
        stages = ["Original", "Clean", "Valid", "Created"]
        if self.report_type == "employees":
            values = [
                report_data.get("total_original", 0),
                report_data.get("total_clean", 0),
                report_data.get("total_valid", 0),
                report_data.get("employees_created", 0),
            ]
        else:
            values = [
                report_data.get("total_original", 0),
                report_data.get("total_clean", 0),
                report_data.get("total_valid", 0),
                report_data.get("sales_created", 0),
            ]

        graphs["pipeline_flow"] = self.create_pipeline_flow_chart(
            stages, values, filename="pipeline_flow.png"
        )

        # Gráfico de validación general
        total_valid = report_data.get("total_valid", 0)
        total_clean = report_data.get("total_clean", 0)
        total_invalid = total_clean - total_valid

        graphs["validation_pie"] = self.create_pie_chart(
            {"Valid": total_valid, "Invalid": total_invalid},
            "General Validation Results",
            filename="validation_pie.png",
        )

        # Specific charts based on report type
        if self.report_type == "employees":
            graphs.update(
                self._generate_employee_graphs(df_original, df_clean, report_data)
            )
        else:
            graphs.update(
                self._generate_sales_graphs(df_original, df_clean, report_data)
            )

        # Detailed validation chart
        if len(validations) > 0:
            validation_results = {}
            for col in validations.columns:
                if col not in ["employee_id", "sale_id", "product_id", "name"]:
                    try:
                        col_data = validations[col].copy()
                        # Convert to boolean, treating None/NaN as False
                        col_data = col_data.apply(
                            lambda x: bool(x) if x is not None else False
                        )
                        true_count = int(col_data.sum())
                        false_count = len(col_data) - true_count
                        if true_count + false_count > 0:
                            validation_results[col[:20]] = (true_count, false_count)
                    except (TypeError, ValueError):
                        continue

            if validation_results:
                graphs["validation_details"] = self.create_validation_chart(
                    validation_results, filename="validation_details.png"
                )

        return graphs

    def _generate_employee_graphs(
        self,
            df_original: pd.DataFrame,
            df_clean: pd.DataFrame,
            report_data: Dict[str, Any],) -> Dict[str, str]:

        """Generate employee-specific charts."""
        graphs = {}

        # Gender distribution
        gender_graph = self.create_gender_distribution(df_original)
        if gender_graph:
            graphs["gender_distribution"] = gender_graph

        # Department distribution
        dept_graph = self.create_department_distribution(df_original)
        if dept_graph:
            graphs["department_distribution"] = dept_graph

        # Age distribution
        age_graph = self.create_age_distribution(df_original)
        if age_graph:
            graphs["age_distribution"] = age_graph

        # Employee activity chart (with/without sales)
        relation_stats = report_data.get("relation_stats", {})
        emp_con_ventas = relation_stats.get("employees_with_sales", 0)
        emp_sin_ventas = relation_stats.get("employees_without_sales", 0)

        if emp_con_ventas + emp_sin_ventas > 0:
            graphs["employee_activity"] = self.create_pie_chart(
                {"With Sales": emp_con_ventas, "Without Sales": emp_sin_ventas},
                "Employee Activity",
                filename="employee_activity.png",
            )

        # Date validation chart
        cleaning_stats = report_data.get("cleaning_stats", {})
        adult_hires = cleaning_stats.get("adult_hires", 0)
        underage_hires = cleaning_stats.get("underage_hires", 0)
        term_before_hire = cleaning_stats.get("terminated_before_hire", 0)

        if adult_hires + underage_hires + term_before_hire > 0:
            graphs["date_validations"] = self.create_bar_chart(
                {
                    "Valid Hiring": adult_hires,
                    "Underage Hiring": underage_hires,
                    "Terminated Before Hire": term_before_hire,
                },
                "Date Validations",
                ylabel="Employees",
                filename="date_validations.png",
            )

        return graphs

    def _generate_sales_graphs(
        self,
            df_original: pd.DataFrame,
            df_clean: pd.DataFrame,
            report_data: Dict[str, Any],) -> Dict[str, str]:

        """Generate sales-specific charts."""
        graphs = {}

        # Status distribution
        status_graph = self.create_status_distribution(df_original)
        if status_graph:
            graphs["status_distribution"] = status_graph

        # Revenue by status
        revenue_graph = self.create_revenue_by_status(df_clean)
        if revenue_graph:
            graphs["revenue_by_status"] = revenue_graph

        # Quantity distribution
        qty_graph = self.create_quantity_distribution(df_original)
        if qty_graph:
            graphs["quantity_distribution"] = qty_graph

        # Price distribution
        price_graph = self.create_price_distribution(df_original)
        if price_graph:
            graphs["price_distribution"] = price_graph

        # Date inconsistencies chart
        cleaning_stats = report_data.get("cleaning_stats", {})
        future_dates = cleaning_stats.get("future_dates", 0)
        sales_before_hire = cleaning_stats.get("sales_before_hire", 0)

        if future_dates + sales_before_hire > 0:
            graphs["date_issues"] = self.create_bar_chart(
                {"Future Dates": future_dates, "Sales Before Hire": sales_before_hire},
                "Date Inconsistencies",
                ylabel="Quantity",
                filename="date_issues.png",
            )

        # Referential integrity chart
        relation_stats = report_data.get("relation_stats", {})
        valid_ids = relation_stats.get("sales_with_valid_employee", 0)
        invalid_ids = relation_stats.get("sales_with_invalid_employee", 0)

        if valid_ids + invalid_ids > 0:
            graphs["referential_integrity"] = self.create_pie_chart(
                {"Valid IDs": valid_ids, "Invalid IDs": invalid_ids},
                "Referential Integrity",
                filename="referential_integrity.png",
            )

        return graphs

    def get_generated_graphs(self) -> List[str]:
        """Returns the list of generated graphs."""
        return self.generated_graphs


def generate_report_graphs(
    report_data: Dict[str, Any],
    output_dir: str = "src/reports/graphs",
    report_type: str = "employees",
) -> Dict[str, str]:
    """
    Wrapper function to generate all graphs for a report.

    Args:
        report_data: Report data
        output_dir: Output directory for the graphs
        report_type: 'employees' or 'sales'

    Returns:
        Dictionary with {graph_name: file_path}
    """
    generator = ReportGraphGenerator(output_dir, report_type)
    return generator.generate_all_graphs(report_data)
