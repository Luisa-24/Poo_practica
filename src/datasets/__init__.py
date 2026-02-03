"""
Módulo de datasets para carga y gestión de datos.
"""
from .dataset import Dataset
from .employees_dataset import EmployeesDataset
from .sales_dataset import SalesDataset

__all__ = ['Dataset', 'EmployeesDataset', 'SalesDataset']
