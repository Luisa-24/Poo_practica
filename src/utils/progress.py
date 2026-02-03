"""This module provides a progress tracking utility for monitoring the
various phases of the data processing pipeline. It defines a
`PipelineProgress` class that uses the `rich` library to display progress bars
and status updates in the console.

Args:
    None. The module defines classes and functions for use in other parts of the application.

Returns:
    None. The module provides functionality for tracking and displaying progress.

Raises:
    None. The module is designed to be used without raising exceptions.

Note:
    - The `PipelineProgress` class can be used as a context manager to automatically
      handle the start and stop of the progress display.

    - Each phase of the pipeline can be started, advanced and completed with dedicated methods.

    - The `pipeline_progress` function provides a convenient way to use the `PipelineProgress` class
      within a `with` statement.
"""

from contextlib import contextmanager
from typing import Any, Generator, cast

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TaskID,
)
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# Phases of the employee and sales data processing pipeline
PIPELINE_PHASES = [
    ("Loading Data", "Loading employee and sales datasets"),
    ("Cleaning Data", "Cleaning and normalizing data fields"),
    ("Validating Data", "Validating data integrity"),
    ("Creating Instances", "Creating Employee and Sale objects"),
    ("Calculating Relations", "Analyzing relationships between datasets"),
    ("Saving CSV Reports", "Exporting cleaned data to CSV files"),
    ("Generating PDF Reports", "Creating PDF reports with LaTeX"),
]


class PipelineProgress:

    def __init__(self, show_header: bool = True):
        self.console = console
        self.show_header = show_header
        self.progress = Progress(
            SpinnerColumn(style="bold cyan"),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(
                bar_width=40, complete_style="green", finished_style="bold green"
            ),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            expand=False,)
        self.tasks: dict[str, TaskID] = {}
        self.phase_descriptions: dict[str, str] = {}
        self._started = False
        self.stats: dict[str, Any] = {}

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish(success=(exc_type is None))
        return False

    def _print_header(self):
        """Print a styled header for the pipeline."""
        header = Panel(
            "[bold white]Employee & Sales Data Processing Pipeline[/bold white]\n"
            "[dim]Processing, validating, and generating reports[/dim]",
            box=box.DOUBLE,
            style="cyan",
            padding=(1, 2),)
        self.console.print(header)
        self.console.print()

    def start(self):
        """Start the progress display."""
        if self._started:
            return
        self._started = True

        if self.show_header:
            self._print_header()

        self.progress.start()
        for name, description in PIPELINE_PHASES:
            task_id = self.progress.add_task(name, total=None, visible=False)
            self.tasks[name] = task_id
            self.phase_descriptions[name] = description

    def start_phase(self, name: str, total: int | None = None):
        """Start a specific phase of the pipeline.

        Args:
            name: The name of the phase (must match a PIPELINE_PHASES entry)
            total: Optional total number of items to process
        """
        if name not in self.tasks:
            return
        task_id = self.tasks[name]
        self.progress.update(task_id, visible=True, total=total)
        self.progress.start_task(task_id)



    def advance(self, name: str, advance: int = 1):
        """Advance the progress of a phase.

        Args:
            name: The name of the phase
            advance: Number of steps to advance (default: 1)
        """
        if name not in self.tasks:
            return
        
        self.progress.advance(cast(TaskID, self.tasks[name]), advance)


    def complete_phase(self, name: str, message: str | None = None):
        """Mark a phase as complete.

        Args:
            name: The name of the phase
            message: Optional completion message to display
        """
        if name not in self.tasks:
            return
        task_id = self.tasks[name]
        task = self.progress.tasks[task_id]
        if task.total is None:
            self.progress.update(task_id, total=1, completed=1)
        else:
            self.progress.update(task_id, completed=task.total)


    def set_stat(self, key: str, value: Any):
        """Store a statistic to be displayed in the summary.

        Args:
            key: The name of the statistic
            value: The value of the statistic
        """
        self.stats[key] = value

    def log_info(self, message: str):
        """Log an informational message.

        Args:
            message: The message to display
        """
        self.console.print(f" {message}")

    def log_success(self, message: str):
        """Log a success message.

        Args:
            message: The message to display
        """
        self.console.print(f"  {message}")

    def log_warning(self, message: str):
        """Log a warning message.

        Args:
            message: The message to display
        """
        self.console.print(f"  {message}")

    def log_error(self, message: str):
        """Log an error message.

        Args:
            message: The message to display
        """
        self.console.print(f"{message}")

    def _print_summary(self):
        """Print a summary table with collected statistics."""
        if not self.stats:
            return

        self.console.print()
        table = Table(
            title="Processing Summary",
            box=box.ROUNDED,
            header_style="bold cyan",
            show_header=True,)
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right", style="green")

        for key, value in self.stats.items():
            table.add_row(key, str(value))

        self.console.print(table)

    def finish(self, success: bool = True):
        """Finish the progress display and show summary.

        Args:
            success: Whether the pipeline completed successfully
        """
        if not self._started:
            return
        self.progress.stop()

        self.console.print()

        if success:
            self.console.print(
                Panel(
                    "[bold green]Pipeline completed successfully![/bold green]",
                    box=box.ROUNDED,
                    style="green",))
        else:
            self.console.print(
                Panel(
                    "[bold red]Pipeline failed![/bold red]",
                    box=box.ROUNDED,
                    style="red",))


@contextmanager
def pipeline_progress(show_header: bool = True,) -> Generator[PipelineProgress, None, None]:
    """Context manager for pipeline progress tracking.

    Args:
        show_header: Whether to display the header panel

    Returns:
        PipelineProgress instance for tracking progress
    """
    progress = PipelineProgress(show_header=show_header)
    with progress:
        yield progress
