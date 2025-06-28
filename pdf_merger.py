import fitz  # PyMuPDF
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PDFMerger:
    def __init__(self):
        pass

    def merge_pdfs(self, pdf_paths, output_path=None):
        """Объединение нескольких PDF файлов в один"""
        try:
            if not pdf_paths:
                return None

            # Если только один файл, возвращаем его путь
            if len(pdf_paths) == 1:
                return pdf_paths[0]

            # Создаем новый PDF документ
            merged_doc = fitz.open()

            # Добавляем каждый PDF в объединенный документ
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    logger.info(f"Adding {pdf_path} to merged document")
                    doc = fitz.open(pdf_path)
                    merged_doc.insert_pdf(doc)
                    doc.close()
                else:
                    logger.warning(f"File not found: {pdf_path}")

            # Генерируем имя для объединенного файла
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(
                    os.path.dirname(pdf_paths[0]),
                    f"merged_{timestamp}.pdf"
                )

            # Сохраняем объединенный документ
            merged_doc.save(output_path)
            merged_doc.close()

            logger.info(f"Successfully merged {len(pdf_paths)} PDFs into {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            return None
