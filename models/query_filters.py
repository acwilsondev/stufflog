"""
This module contains the QueryFilter class, which is used to encapsulate filtering
parameters for querying stufflog entries.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class QueryFilter:
    """
    A class to encapsulate filtering parameters for querying stufflog entries.

    greater_than: Filter for entries with rating greater than this value.
    less_than: Filter for entries with rating less than this value.
    after: Filter for entries with datetime after this value.
    before: Filter for entries with datetime before this value.
    """
    greater_than: Optional[int] = None
    less_than: Optional[int] = None
    after: Optional[str] = None
    before: Optional[str] = None
