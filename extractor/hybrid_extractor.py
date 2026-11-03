# extractor/hybrid_extractor.py

from extractor.text_extractor import TextExtractor
from extractor.ocr_extractor import OCRExtractor


class HybridExtractor:

    def __init__(self):

        self.text_extractor = TextExtractor()
        self.ocr_extractor = OCRExtractor()

                 

    def extract(self, pdf_path: str):

        document = self.text_extractor.extract(
            pdf_path
        )

        total_words = sum(
            len(page.words)
            for page in document.pages
        )

        print(f"{pdf_path} -> total_words = {total_words}")    


        if total_words > 0:

            print(
                f"[TEXT MODE] {pdf_path}"
            )

            return document

        print(
            f"[OCR MODE] {pdf_path}"
        )

        return self.ocr_extractor.extract(
            pdf_path
        )