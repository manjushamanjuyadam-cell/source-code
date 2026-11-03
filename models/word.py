from dataclasses import dataclass

@dataclass
class Word:
    text: str
    x0: float
    top: float
    x1: float
    bottom: float