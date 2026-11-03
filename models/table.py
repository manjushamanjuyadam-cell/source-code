from dataclasses import dataclass, field
from typing import List


@dataclass
class Table:
    rows: List[List[str]]
    bbox: tuple | None = None