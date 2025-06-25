class PDFSurge {
    constructor() {
        this.files = [];
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.processBtn = document.getElementById('processBtn');
        this.reportSection = document.getElementById('reportSection');
        this.reportText = document.getElementById('reportText');
        this.copyBtn = document.getElementById('copyBtn');
        this.newReportBtn = document.getElementById('newReportBtn');
        this.loading = document.getElementById('loading');
    }

    bindEvents() {
        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        // Click to upload
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // Process button
        this.processBtn.addEventListener('click', () => {
            this.processFiles();
        });

        // Copy button
        this.copyBtn.addEventListener('click', () => {
            this.copyToClipboard();
        });

        // New report button
        this.newReportBtn.addEventListener('click', () => {
            this.resetForm();
        });
    }

    handleFiles(files) {
        const pdfFiles = Array.from(files).filter(file =>
            file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
        );

        if (pdfFiles.length === 0) {
            this.showError('Пожалуйста, выберите PDF файлы');
            return;
        }

        // Добавляем новые файлы к существующим, избегая дублирования
        pdfFiles.forEach(newFile => {
            const isDuplicate = this.files.some(existingFile =>
                existingFile.name === newFile.name &&
                existingFile.size === newFile.size
            );

            if (!isDuplicate) {
                this.files.push(newFile);
            }
        });

        this.displayFiles();
        this.processBtn.disabled = this.files.length === 0;

        // Показываем сообщение о добавленных файлах
        const addedCount = pdfFiles.length;
        const duplicateCount = pdfFiles.length - pdfFiles.filter(newFile =>
            !this.files.some((existingFile, index) =>
                index >= this.files.length - addedCount &&
                existingFile.name === newFile.name &&
                existingFile.size === newFile.size
            )
        ).length;

        if (duplicateCount > 0) {
            this.showInfo(`Добавлено файлов: ${addedCount - duplicateCount}. Пропущено дублей: ${duplicateCount}`);
        } else {
            this.showInfo(`Добавлено файлов: ${addedCount}`);
        }
    }

    displayFiles() {
        this.fileList.innerHTML = '';

        if (this.files.length === 0) {
            return;
        }

        // Добавляем заголовок со счетчиком файлов
        const header = document.createElement('div');
        header.className = 'files-header';
        header.innerHTML = `
            <h4>Выбранные файлы (${this.files.length})</h4>
            <button class="btn-clear-all" onclick="pdfSurge.clearAllFiles()">Очистить все</button>
        `;
        this.fileList.appendChild(header);

        this.files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';

            const fileSize = (file.size / 1024 / 1024).toFixed(2);

            fileItem.innerHTML = `
                <div class="file-info">
                    <span class="file-icon">📄</span>
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${fileSize} MB</span>
                </div>
                <button class="file-remove" onclick="pdfSurge.removeFile(${index})">×</button>
            `;

            this.fileList.appendChild(fileItem);
        });
    }

    removeFile(index) {
        this.files.splice(index, 1);
        this.displayFiles();
        this.processBtn.disabled = this.files.length === 0;
        this.showInfo('Файл удален');
    }

    clearAllFiles() {
        this.files = [];
        this.displayFiles();
        this.processBtn.disabled = true;
        this.fileInput.value = '';
        this.showInfo('Все файлы удалены');
    }

    async processFiles() {
        if (this.files.length === 0) return;

        this.showLoading();

        const formData = new FormData();
        this.files.forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.showReport(data.report);
            } else {
                this.showError(data.error || 'Произошла ошибка при обработке файлов');
            }
        } catch (error) {
            this.showError('Ошибка соединения: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    showReport(report) {
        this.reportText.value = report;
        this.reportText.placeholder = '';

        // Показываем кнопки управления отчетом
        this.copyBtn.style.display = 'inline-block';
        this.newReportBtn.style.display = 'inline-block';

        // Убираем класс hidden если он есть
        this.reportSection.classList.remove('hidden');
    }

    async copyToClipboard() {
        try {
            await navigator.clipboard.writeText(this.reportText.value);
            this.showSuccess('Отчет скопирован в буфер обмена');
        } catch (error) {
            // Fallback для старых браузеров
            this.reportText.select();
            document.execCommand('copy');
            this.showSuccess('Отчет скопирован в буфер обмена');
        }
    }

    resetForm() {
        this.files = [];
        this.fileList.innerHTML = '';
        this.processBtn.disabled = true;
        this.fileInput.value = '';

        // Очищаем отчет и скрываем кнопки
        this.reportText.value = '';
        this.reportText.placeholder = 'Отчет появится здесь после обработки файлов...';
        this.copyBtn.style.display = 'none';
        this.newReportBtn.style.display = 'none';

        this.removeMessages();
    }

    showLoading() {
        this.loading.style.display = 'block';
        this.processBtn.disabled = true;
    }

    hideLoading() {
        this.loading.style.display = 'none';
        this.processBtn.disabled = false;
    }

    showError(message) {
        this.removeMessages();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = message;
        this.uploadArea.parentNode.insertBefore(errorDiv, this.uploadArea.nextSibling);
    }

    showSuccess(message) {
        this.removeMessages();
        const successDiv = document.createElement('div');
        successDiv.className = 'success';
        successDiv.textContent = message;
        this.reportSection.appendChild(successDiv);

        // Удаляем сообщение через 3 секунды
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 3000);
    }

    showInfo(message) {
        this.removeMessages();
        const infoDiv = document.createElement('div');
        infoDiv.className = 'info';
        infoDiv.textContent = message;
        this.uploadArea.parentNode.insertBefore(infoDiv, this.uploadArea.nextSibling);

        // Удаляем сообщение через 3 секунды
        setTimeout(() => {
            if (infoDiv.parentNode) {
                infoDiv.parentNode.removeChild(infoDiv);
            }
        }, 3000);
    }

    removeMessages() {
        const messages = document.querySelectorAll('.error, .success, .info');
        messages.forEach(msg => {
            if (msg.parentNode) {
                msg.parentNode.removeChild(msg);
            }
        });
    }
}

// Инициализация приложения
const pdfSurge = new PDFSurge();