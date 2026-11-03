import pdfplumber

from extractor.base_extractor import BaseExtractor
from models.document import Document
from models.page import Page
from models.word import Word


class TextExtractor(BaseExtractor):

    def extract(self, pdf_path: str) -> Document:

        document = Document()

        with pdfplumber.open(pdf_path) as pdf:

            for page_index, pdf_page in enumerate(pdf.pages):

                page = Page(
                    page_number=page_index + 1,
                    width=pdf_page.width,
                    height=pdf_page.height
                )

                words = pdf_page.extract_words(
                    x_tolerance=2,
                    y_tolerance=2
                )

                for item in words:

                    word = Word(
                        text=item["text"],
                        x0=item["x0"],
                        top=item["top"],
                        x1=item["x1"],
                        bottom=item["bottom"]
                    )

                    page.text = pdf_page.extract_text() or ""

                document.pages.append(page)

        return document