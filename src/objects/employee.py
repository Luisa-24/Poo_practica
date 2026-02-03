# ESTANDAR
import sys
import os
from datetime import datetime
from dataclasses import dataclass

# Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@dataclass
class Employee:
    """Represents an individual employee with personal and employment data.

    Arg:
        name: Full name of the employee.

    Returns:
        Employee: An instance of the Employee class."""

    _name: str
    _gender: str
    _nationality: str
    _department: str
    _position: str
    _age: int
    _birthdate: datetime
    _email: str
    _phone: str
    _address: str
    _hire_date: datetime
    _contract_type: str
    _employee_id: str
    _salary: float
    _termination_date: datetime
