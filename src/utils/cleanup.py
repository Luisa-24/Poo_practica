"""
Clean up specific folders and files used in previous pipeline runs.

This module provides utilities for cleaning output files and folders
from the data processing pipeline, including CSV outputs, PDF reports,
and generated graphs.

Args:
    script_dir (Path): The base directory of the script where data folders are located.

Returns:
    None. The specified folders and files are deleted if they exist.

Raises:
    None. Any errors during deletion are silently ignored.

Note:
    - Folders cleaned: data/outputs, src/reports/output/graphs
    - Files cleaned: cleaned CSV files, generated PDF and TEX reports
"""

import shutil
from pathlib import Path
from typing import List, Any, Dict

from rich.table import Table
from rich import box
from .progress import console


def cleanup_folders(
    script_dir: Path,
    clean_csv: bool = True,
    clean_reports: bool = True,
    clean_graphs: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Clean up output folders and files from previous pipeline runs.

    Args:
        script_dir: The base directory of the project
        clean_csv: Whether to clean CSV output files
        clean_reports: Whether to clean PDF/TEX report files
        clean_graphs: Whether to clean generated graph files
        verbose: Whether to display detailed cleanup information

    Returns:
        Dictionary with cleanup statistics
    """
    stats: Dict[str, Any] = {"files_deleted": 0, "folders_cleaned": 0, "errors": []}

    deleted_items: List[str] = []

    # Define folders to clean
    folders_to_clean = []

    if clean_graphs:
        folders_to_clean.append(script_dir / "src" / "reports" / "output" / "graphs")

    # Define files to clean
    files_to_clean = []

    if clean_csv:
        files_to_clean.extend(
            [
                script_dir / "data" / "outputs" / "employee_data_clean.csv",
                script_dir / "data" / "outputs" / "sales_data_clean.csv",
            ])

    if clean_reports:
        files_to_clean.extend(
            [
                script_dir / "src" / "reports" / "output" / "report_employees_en.pdf",
                script_dir / "src" / "reports" / "output" / "report_employees_en.tex",
                script_dir / "src" / "reports" / "output" / "report_sales_en.pdf",
                script_dir / "src" / "reports" / "output" / "report_sales_en.tex",
            ])

    with console.status("Cleaning previous run files", spinner="dots"):
        # Clean folders
        for folder in folders_to_clean:
            if folder.exists():
                try:
                    for item in folder.iterdir():
                        if item.is_file():
                            item.unlink()
                            deleted_items.append(str(item.name))
                            stats["files_deleted"] += 1
                        elif item.is_dir():
                            shutil.rmtree(item)
                            deleted_items.append(str(item.name) + "/")
                            stats["folders_cleaned"] += 1
                except Exception as e:
                    stats["errors"].append(f"Error cleaning {folder}: {e}")
            else:
                try:
                    folder.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    stats["errors"].append(f"Error creating {folder}: {e}")

        # Clean individual files
        for file in files_to_clean:
            if file.exists():
                try:
                    file.unlink()
                    deleted_items.append(str(file.name))
                    stats["files_deleted"] += 1
                except Exception as e:
                    stats["errors"].append(f"Error deleting {file.name}: {e}")

    # Display results
    if verbose:
        _display_cleanup_results(deleted_items, stats)

    return stats


def _display_cleanup_results(deleted_items: List[str], stats: dict):
    """Display cleanup results in a formatted table."""

    if deleted_items:
        table = Table(
            title="Cleanup Results",
            box=box.ROUNDED,
            header_style="bold cyan",
            show_header=True,)
        table.add_column("Item Deleted", style="dim")
        table.add_column("Status", justify="center", style="green")

        for item in deleted_items:
            table.add_row(item, "Deleted")

        console.print(table)
        console.print()

    # Summary
    if stats["files_deleted"] > 0 or stats["folders_cleaned"] > 0:
        console.print(
            f"[green]Cleanup complete:[/green] "
            f"[bold]{stats['files_deleted']}[/bold] files, "
            f"[bold]{stats['folders_cleaned']}[/bold] folders cleaned"
        )
    else:
        console.print("No files to clean - workspace is already clean")

    # Show errors if any
    if stats["errors"]:
        console.print()
        for error in stats["errors"]:
            console.print(f"{error}")

    console.print()


def ensure_output_directories(script_dir: Path) -> None:
    """
    Ensure all necessary output directories exist.

    Args:
        script_dir: The base directory of the project
    """
    directories = [
        script_dir / "data" / "outputs",
        script_dir / "src" / "reports" / "output",
        script_dir / "src" / "reports" / "output" / "graphs",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
