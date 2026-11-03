from dataclasses import dataclass, field
from typing import List
import models

from models.word import Word

@dataclass
class Line:
    words: List[Word] = field(default_factory=list)

    @property
    def text(self):
        return " ".join(word.text for word in self.words)