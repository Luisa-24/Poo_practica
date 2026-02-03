"""Utilidades compartidas del proyecto."""

from .logger import get_logger, setup_logging
from .progress import (
    PipelineProgress,
    pipeline_progress,
    console,
    PIPELINE_PHASES,
)
from .cleanup import (
    cleanup_folders,
    ensure_output_directories,
)

__all__ = [
    'get_logger',
    'setup_logging',
    'PipelineProgress',
    'pipeline_progress',
    'console',
    'PIPELINE_PHASES',
    'cleanup_folders',
    'ensure_output_directories',
]
