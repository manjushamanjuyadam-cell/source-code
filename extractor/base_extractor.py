from abc import ABC, abstractmethod

from models.document import Document


class BaseExtractor(ABC):

    @abstractmethod
    def extract(self, pdf_path: str) -> Document:
        pass