# extractor/ocr_extractor.py

import pdfplumber
import pytesseract

from models.document import Document
from models.page import Page
from extractor.base_extractor import BaseExtractor


class OCRExtractor(BaseExtractor):

    def extract(self, pdf_path: str) -> Document:

        document = Document()

        with pdfplumber.open(pdf_path) as pdf:

            for page_index, pdf_page in enumerate(pdf.pages):

                page = Page(
                    page_number=page_index + 1,
                    width=pdf_page.width,
                    height=pdf_page.height
                )

                image = pdf_page.to_image(
                    resolution=300
                )

                text = pytesseract.image_to_string(
                    image.original
                )

                page.ocr_text = text

                document.pages.append(page)

        return document