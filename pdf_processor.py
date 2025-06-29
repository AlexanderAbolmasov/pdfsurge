import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image
import io
import logging
import os
from deskew_processor import DeskewProcessor
import subprocess

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        # В Docker контейнере Tesseract всегда находится по стандартному пути
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
        logger.info("Tesseract configured for Docker container at /usr/bin/tesseract")

        # Диагностика и получение доступных языков
        self.available_languages = self.get_available_languages()
        logger.info(f"Available OCR languages: {self.available_languages}")

        self.deskew_processor = DeskewProcessor()

    def get_available_languages(self):
        """Получить список доступных языков Tesseract"""
        try:
            result = subprocess.run(['tesseract', '--list-langs'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                langs = [line.strip() for line in lines[1:] if line.strip()]

                # Проверяем наличие нужных языков
                available = []
                for lang in ['rus', 'eng']:
                    if lang in langs:
                        available.append(lang)

                return available if available else ['eng']  # fallback к английскому
            else:
                logger.warning(f"Cannot get languages: {result.stderr}")
                return ['eng']
        except Exception as e:
            logger.error(f"Error getting languages: {e}")
            return ['eng']

    def extract_text_pymupdf(self, pdf_path):
        """Извлечение текста с помощью PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text.strip():
                    text += f"\n--- Страница {page_num + 1} ---\n{page_text}\n"
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
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text += f"\n--- Страница {page_num + 1} ---\n{page_text}\n"
            return text.strip()
        except Exception as e:
            logger.error(f"pdfplumber error: {e}")
            return ""

    def extract_text_ocr_with_deskew(self, pdf_path):
        """Извлечение текста с помощью OCR с предварительным дескьюингом"""
        try:
            # Определяем языки для OCR
            lang_param = '+'.join(self.available_languages) if self.available_languages else None

            doc = fitz.open(pdf_path)
            text = ""

            for page_num in range(doc.page_count):
                page = doc[page_num]
                # Применяем дескьюинг
                deskewed_image, skew_angle = self.deskew_processor.deskew_pdf_page(page)
                logger.info(f"Page {page_num + 1}: corrected skew by {skew_angle:.2f} degrees")

                # OCR с доступными языками
                try:
                    if lang_param:
                        page_text = pytesseract.image_to_string(
                            deskewed_image,
                            lang=lang_param,
                            config='--oem 3 --psm 6'
                        )
                    else:
                        # Fallback без языка
                        page_text = pytesseract.image_to_string(
                            deskewed_image,
                            config='--oem 3 --psm 6'
                        )

                    if page_text.strip():
                        text += f"\n--- Страница {page_num + 1} ---\n{page_text}\n"
                        logger.info(f"Page {page_num + 1}: extracted {len(page_text)} characters")

                except Exception as ocr_error:
                    logger.error(f"OCR error on page {page_num + 1}: {ocr_error}")
                    continue

            doc.close()
            return text.strip()

        except Exception as e:
            logger.error(f"OCR with deskew error: {e}")
            return ""

    def extract_text_from_pdf(self, pdf_path):
        """Последовательное извлечение текста разными методами"""
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
        """Обработка нескольких PDF файлов и объединение в один текст"""
        combined_text = ""
        successful_extractions = 0

        logger.info(f"Processing {len(pdf_paths)} PDF files")

        for i, pdf_path in enumerate(pdf_paths, 1):
            if os.path.exists(pdf_path):
                logger.info(f"Processing file {i}/{len(pdf_paths)}: {os.path.basename(pdf_path)}")

                text = self.extract_text_from_pdf(pdf_path)
                if text and text.strip():
                    # Добавляем заголовок документа
                    combined_text += f"\n\n{'=' * 60}\n"
                    combined_text += f"ДОКУМЕНТ {i}: {os.path.basename(pdf_path)}\n"
                    combined_text += f"{'=' * 60}\n\n"
                    combined_text += text
                    successful_extractions += 1
                    logger.info(f"Successfully extracted {len(text)} characters from {os.path.basename(pdf_path)}")
                else:
                    logger.warning(f"No text extracted from {os.path.basename(pdf_path)}")
            else:
                logger.error(f"File not found: {pdf_path}")

        logger.info(f"Successfully processed {successful_extractions}/{len(pdf_paths)} files")

        if combined_text.strip():
            # Добавляем общий заголовок
            final_text = f"ОБЪЕДИНЕННЫЙ ТЕКСТ ИЗ {successful_extractions} ДОКУМЕНТОВ\n"
            final_text += f"Обработано: {', '.join([os.path.basename(p) for p in pdf_paths])}\n"
            final_text += f"{'=' * 80}\n"
            final_text += combined_text

            # Сохраняем объединенный текст в файл для отладки
            try:
                debug_file = os.path.join('uploads', 'combined_text_debug.txt')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(final_text)
                logger.info(f"Combined text saved to {debug_file} ({len(final_text)} characters)")
            except Exception as e:
                logger.error(f"Cannot save debug file: {e}")

            return final_text
        else:
            logger.error("No text was extracted from any PDF files")
            return ""

    def get_text_summary(self, text):
        """Получить краткую сводку о извлеченном тексте"""
        if not text:
            return "Текст не извлечен"

        lines = text.split('\n')
        words = text.split()
        chars = len(text)

        return f"Извлечено: {len(lines)} строк, {len(words)} слов, {chars} символов"