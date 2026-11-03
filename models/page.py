from dataclasses import dataclass, field
from typing import List

from models.word import Word
from models.line import Line
from models.paragraph import Paragraph
from models.table import Table
from models.block import Block


@dataclass
class Page:

    page_number: int
    width: float
    height: float

    words: List[Word] = field(default_factory=list)
    lines: List[Line] = field(default_factory=list)
    blocks: List[Block] = field(default_factory=list)

    paragraphs: List[Paragraph] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    text: str = ""
