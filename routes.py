import logging
import os
import uuid
from flask import render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from yandex_gpt_service import YandexGPTService
from pdf_merger import PDFMerger
from pdf_processor import PDFProcessor
from prompts import get_system_prompt, get_user_prompt

logger = logging.getLogger(__name__)


def init_routes(app):
    pdf_processor = PDFProcessor()
    ai_service = YandexGPTService()
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

            # ИСПРАВЛЕННОЕ СОХРАНЕНИЕ: убираем дублирование
            uploaded_files = []
            session_id = str(uuid.uuid4())

            for i, file in enumerate(files):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{session_id}_{i}_{filename}"  # Добавляем индекс для уникальности
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    uploaded_files.append(filepath)
                    logger.info(f"Saved file {i + 1}: {unique_filename}")

            logger.info(f"Successfully saved {len(uploaded_files)} unique files")

            # ЛОГИКА ОБЪЕДИНЕНИЯ: используем PDF merger для нескольких файлов
            if len(uploaded_files) > 1:
                logger.info(f"Multiple files detected - using PDF merger for {len(uploaded_files)} files")

                # Объединяем PDF файлы физически
                merged_pdf_path = pdf_merger.merge_pdfs(uploaded_files)
                if not merged_pdf_path:
                    raise Exception("Failed to merge PDF files")

                logger.info(f"Successfully merged PDFs into: {os.path.basename(merged_pdf_path)}")

                # Извлекаем текст из объединенного PDF
                combined_text = pdf_processor.extract_text_from_pdf(merged_pdf_path)

                # Файлы для очистки
                files_to_cleanup = uploaded_files + [merged_pdf_path]

            else:
                logger.info("Single file detected - processing directly")

                # Для одного файла обрабатываем напрямую
                combined_text = pdf_processor.extract_text_from_pdf(uploaded_files[0])

                # Файлы для очистки
                files_to_cleanup = uploaded_files

            # Проверяем успешность извлечения текста
            if not combined_text or len(combined_text.strip()) < 50:
                # Очищаем файлы при ошибке
                for filepath in files_to_cleanup:
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except Exception as cleanup_error:
                        logger.error(f"Cannot cleanup {filepath}: {cleanup_error}")

                return jsonify({'error': 'Не удалось извлечь достаточно текста из PDF файлов'}), 400

            logger.info(f"Successfully extracted {len(combined_text)} characters from {len(uploaded_files)} file(s)")

            # Сохраняем объединенный текст для отладки
            try:
                debug_file = os.path.join(current_app.config['UPLOAD_FOLDER'], f'combined_text_debug_{session_id}.txt')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(combined_text)
                logger.info(f"Combined text saved to {debug_file}")
            except Exception as e:
                logger.error(f"Cannot save debug file: {e}")

            # Генерируем отчет из объединенного текста
            try:
                system_prompt = get_system_prompt()
                user_prompt = get_user_prompt(combined_text)

                logger.info(f"Sending {len(combined_text)} characters to Yandex GPT for analysis")
                report = ai_service.generate_report(system_prompt, user_prompt)
                logger.info(f"Received report with {len(report)} characters from Yandex GPT")

            except Exception as gpt_error:
                logger.error(f"Yandex GPT error: {gpt_error}")
                # Очищаем файлы при ошибке GPT
                for filepath in files_to_cleanup:
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except:
                        pass
                return jsonify({'error': f'Ошибка генерации отчета: {str(gpt_error)}'}), 500

            # Удаляем загруженные файлы после успешной обработки
            for filepath in files_to_cleanup:
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        logger.info(f"Cleaned up: {os.path.basename(filepath)}")
                except Exception as e:
                    logger.error(f"Cannot remove {filepath}: {e}")

            # Проверяем на ошибки в отчете
            if report.startswith("ОШИБКА:"):
                logger.error(f"Yandex GPT returned error: {report}")
                return jsonify({'error': report}), 400

            logger.info("Successfully completed file processing and report generation")
            return jsonify({
                'report': report,
                'files_processed': len(uploaded_files),
                'total_characters': len(combined_text),
                'processing_method': 'merged' if len(uploaded_files) > 1 else 'single'
            })

        except Exception as e:
            logger.error(f"Upload error: {e}")
            # Экстренная очистка при любой ошибке
            try:
                if 'uploaded_files' in locals():
                    for filepath in uploaded_files:
                        if os.path.exists(filepath):
                            os.remove(filepath)
            except:
                pass
            return jsonify({'error': f'Ошибка обработки: {str(e)}'}), 500
