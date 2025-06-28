import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import io
import logging
import os
from deskew_processor import DeskewProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        # Настройка Tesseract для Mac
        pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
        self.deskew_processor = DeskewProcessor()

    def extract_text_pymupdf(self, pdf_path):
        """Извлечение текста с помощью PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            logger.error(f"PyMuPDF error: {e}")
            return ""

    def extract_text_pdfplumber(self, pdf_path):
        """Извлечение текста с помощью pdfplumber"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"pdfplumber error: {e}")
            return ""

    def extract_text_ocr(self, pdf_path):
        """Извлечение текста с помощью OCR"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                # OCR с русским языком
                page_text = pytesseract.image_to_string(img, lang='rus+eng')
                text += page_text + "\n"
            doc.close()
            return text.strip()
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""

    def extract_text_ocr_with_deskew(self, pdf_path):
        """Извлечение текста с помощью OCR с предварительным дескьюингом"""
        try:
            doc = fitz.open(pdf_path)
            text = ""

            for page_num in range(doc.page_count):
                page = doc[page_num]

                # Применяем дескьюинг
                deskewed_image, skew_angle = self.deskew_processor.deskew_pdf_page(page)
                logger.info(f"Page {page_num + 1}: corrected skew by {skew_angle:.2f} degrees")

                # OCR с русским языком
                page_text = pytesseract.image_to_string(deskewed_image, lang='rus+eng')
                text += page_text + "\n"

            doc.close()
            return text.strip()

        except Exception as e:
            logger.error(f"OCR with deskew error: {e}")
            return ""

    def extract_text_from_pdf(self, pdf_path):
        """Последовательное извлечение текста разными методами с дескьюингом"""
        logger.info(f"Processing PDF: {pdf_path}")

        # Метод 1: PyMuPDF
        text = self.extract_text_pymupdf(pdf_path)
        if len(text) > 100:
            logger.info("Text extracted successfully with PyMuPDF")
            return text

        # Метод 2: pdfplumber
        text = self.extract_text_pdfplumber(pdf_path)
        if len(text) > 100:
            logger.info("Text extracted successfully with pdfplumber")
            return text

        # Метод 3: OCR с дескьюингом
        logger.info("Trying OCR extraction with deskewing...")
        text = self.extract_text_ocr_with_deskew(pdf_path)
        if len(text) > 50:
            logger.info("Text extracted successfully with OCR and deskewing")
            return text

        logger.warning("Failed to extract meaningful text from PDF")
        return ""

    def process_multiple_pdfs(self, pdf_paths):
        """Обработка нескольких PDF файлов"""
        all_text = ""
        for pdf_path in pdf_paths:
            if os.path.exists(pdf_path):
                text = self.extract_text_from_pdf(pdf_path)
                if text:
                    all_text += f"\n\n=== ДОКУМЕНТ: {os.path.basename(pdf_path)} ===\n\n"
                    all_text += text
                else:
                    logger.warning(f"No text extracted from {pdf_path}")

        return all_text.strip()
