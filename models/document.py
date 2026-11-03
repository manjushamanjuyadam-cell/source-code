from dataclasses import dataclass, field
from typing import List

from models.page import Page

@dataclass
class Document:
    pages: List[Page] = field(default_factory=list)