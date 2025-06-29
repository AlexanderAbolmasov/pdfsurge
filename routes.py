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

            # Сохраняем файлы
            uploaded_files = []
            session_id = str(uuid.uuid4())

            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filename = f"{session_id}_{filename}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    uploaded_files.append(filepath)
                    logger.info(f"Saved file: {filename}")

            # ИСПРАВЛЕННАЯ ЛОГИКА: Извлекаем текст из каждого файла и объединяем
            logger.info(f"Processing {len(uploaded_files)} PDF files for text extraction")

            all_texts = []
            for i, pdf_path in enumerate(uploaded_files, 1):
                logger.info(f"Extracting text from file {i}/{len(uploaded_files)}: {os.path.basename(pdf_path)}")
                text = pdf_processor.extract_text_from_pdf(pdf_path)

                if text and text.strip():
                    # Добавляем заголовок для каждого документа
                    document_text = f"\n\n{'=' * 60}\n"
                    document_text += f"ДОКУМЕНТ {i}: {os.path.basename(pdf_path)}\n"
                    document_text += f"{'=' * 60}\n\n"
                    document_text += text
                    all_texts.append(document_text)
                    logger.info(f"Successfully extracted {len(text)} characters from {os.path.basename(pdf_path)}")
                else:
                    logger.warning(f"No text extracted from {os.path.basename(pdf_path)}")

            if not all_texts:
                # Удаляем загруженные файлы
                for filepath in uploaded_files:
                    try:
                        os.remove(filepath)
                    except:
                        pass
                return jsonify({'error': 'Не удалось извлечь текст ни из одного PDF файла'}), 400

            # Объединяем все тексты
            if len(all_texts) == 1:
                combined_text = f"АНАЛИЗ ДОКУМЕНТА\n{'=' * 80}\n{all_texts[0]}"
            else:
                combined_text = f"ОБЪЕДИНЕННЫЙ АНАЛИЗ {len(all_texts)} ДОКУМЕНТОВ\n"
                combined_text += f"{'=' * 80}\n"
                combined_text += "".join(all_texts)

            logger.info(
                f"Successfully combined text from {len(all_texts)} files, total: {len(combined_text)} characters")

            # Сохраняем объединенный текст для отладки
            try:
                debug_file = os.path.join(current_app.config['UPLOAD_FOLDER'], f'combined_text_debug_{session_id}.txt')
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(combined_text)
                logger.info(f"Combined text saved to {debug_file}")
            except Exception as e:
                logger.error(f"Cannot save debug file: {e}")

            # Генерируем отчет из объединенного текста
            system_prompt = get_system_prompt()
            user_prompt = get_user_prompt(combined_text)

            logger.info(f"Sending {len(combined_text)} characters to Yandex GPT for analysis")
            report = ai_service.generate_report(system_prompt, user_prompt)
            logger.info(f"Received report with {len(report)} characters from Yandex GPT")

            # Удаляем загруженные файлы после обработки
            for filepath in uploaded_files:
                try:
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
                'texts_combined': len(all_texts),
                'total_characters': len(combined_text)
            })

        except Exception as e:
            logger.error(f"Upload error: {e}")
            return jsonify({'error': f'Ошибка обработки: {str(e)}'}), 500