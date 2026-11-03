from dataclasses import dataclass, field
from typing import List

from models.line import Line


@dataclass
class Block:
    lines: List[Line] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(
            line.text.strip()
            for line in self.lines
        )