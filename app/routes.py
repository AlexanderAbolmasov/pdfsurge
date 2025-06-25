import logging
import os
import uuid

from flask import render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename

from .grok_service import GrokService
from .pdf_merger import PDFMerger
from .pdf_processor import PDFProcessor
from .prompts import get_system_prompt, get_user_prompt

logger = logging.getLogger(__name__)


def init_routes(app):
    pdf_processor = PDFProcessor()
    ai_service = GrokService()
    pdf_merger = PDFMerger()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload_files():
        try:
            if 'files' not in request.files:
                return jsonify({'error': 'Не выбраны файлы'}), 400

            files = request.files.getlist('files')
            if not files or all(f.filename == '' for f in files):
                return jsonify({'error': 'Не выбраны файлы'}), 400

            # Проверяем, что все файлы - PDF
            for file in files:
                if not file.filename.lower().endswith('.pdf'):
                    return jsonify({'error': f'Файл {file.filename} не является PDF'}), 400

            # Сохраняем файлы
            uploaded_files = []
            session_id = str(uuid.uuid4())
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    # Добавляем session_id к имени файла для уникальности
                    filename = f"{session_id}_{filename}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    uploaded_files.append(filepath)

            # НОВАЯ ЛОГИКА: Объединяем PDF файлы если их больше одного
            if len(uploaded_files) > 1:
                logger.info(f"Merging {len(uploaded_files)} PDF files")
                merged_pdf_path = pdf_merger.merge_pdfs(uploaded_files)

                if merged_pdf_path:
                    # Извлекаем текст из объединенного PDF
                    all_text = pdf_processor.extract_text_from_pdf(merged_pdf_path)

                    # Удаляем исходные файлы, оставляем только объединенный
                    files_to_cleanup = uploaded_files.copy()
                    files_to_cleanup.append(merged_pdf_path)  # Добавляем объединенный файл для удаления
                else:
                    # Если объединение не удалось, используем старый метод
                    logger.warning("PDF merging failed, using individual processing")
                    all_text = pdf_processor.process_multiple_pdfs(uploaded_files)
                    files_to_cleanup = uploaded_files
            else:
                # Если файл один, обрабатываем как обычно
                all_text = pdf_processor.extract_text_from_pdf(uploaded_files[0])
                files_to_cleanup = uploaded_files

            if not all_text:
                # Удаляем загруженные файлы
                for filepath in files_to_cleanup:
                    try:
                        os.remove(filepath)
                    except:
                        pass
                return jsonify({'error': 'Не удалось извлечь текст из PDF файлов'}), 400

            # Генерируем отчет
            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt(all_text)
            report = ai_service.generate_report(system_prompt, user_prompt)

            # Удаляем загруженные файлы после обработки
            for filepath in files_to_cleanup:
                try:
                    os.remove(filepath)
                except:
                    pass

            # Проверяем на ошибки в отчете
            if report.startswith("ОШИБКА:"):
                return jsonify({'error': report}), 400

            return jsonify({'report': report})

        except Exception as e:
            logger.error(f"Upload error: {e}")
            return jsonify({'error': f'Ошибка обработки: {str(e)}'}), 500
