from dataclasses import dataclass

@dataclass
class Difference:
    page: int
    line_number: int
    expected: str
    actual: str