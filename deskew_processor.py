import cv2
import numpy as np
import fitz
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)


class DeskewProcessor:
    def __init__(self):
        self.angle_threshold = 0.5  # Минимальный угол для коррекции

    def detect_skew_angle(self, image):
        """Определение угла наклона изображения"""
        # Преобразование в градации серого
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Применение размытия и бинаризации
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Инвертирование для лучшего обнаружения текста
        binary = cv2.bitwise_not(binary)

        # Поиск контуров
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        angles = []
        for contour in contours:
            # Фильтрация мелких контуров
            if cv2.contourArea(contour) < 100:
                continue

            # Получение минимального прямоугольника
            rect = cv2.minAreaRect(contour)
            angle = rect[2]

            # Нормализация угла
            if angle < -45:
                angle += 90
            elif angle > 45:
                angle -= 90

            angles.append(angle)

        if not angles:
            return 0

        # Возвращаем медианный угол
        return np.median(angles)

    def rotate_image(self, image, angle):
        """Поворот изображения на заданный угол"""
        if abs(angle) < self.angle_threshold:
            return image

        height, width = image.shape[:2]
        center = (width // 2, height // 2)

        # Матрица поворота
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Вычисление новых размеров
        cos_angle = abs(rotation_matrix[0, 0])
        sin_angle = abs(rotation_matrix[0, 1])
        new_width = int((height * sin_angle) + (width * cos_angle))
        new_height = int((height * cos_angle) + (width * sin_angle))

        # Корректировка матрицы для центрирования
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]

        # Применение поворота
        rotated = cv2.warpAffine(image, rotation_matrix, (new_width, new_height),
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated

    def deskew_pdf_page(self, pdf_page):
        """Дескьюинг страницы PDF"""
        try:
            # Конвертация страницы в изображение
            pix = pdf_page.get_pixmap(matrix=fitz.Matrix(1.0, 1.0))  # Увеличиваем разрешение (уменьшил после деплоя)
            img_data = pix.tobytes("png")

            # Преобразование в OpenCV формат
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # ДОБАВЛЯЕМ: Проверка размера изображения
            height, width = image.shape[:2]
            if width > 3000 or height > 3000:
                # Уменьшаем слишком большие изображения
                scale = min(3000 / width, 3000 / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")

            # Определение угла наклона
            skew_angle = self.detect_skew_angle(image)
            logger.info(f"Detected skew angle: {skew_angle:.2f} degrees")

            # Поворот изображения
            deskewed_image = self.rotate_image(image, -skew_angle)

            # Конвертация обратно в PIL Image
            _, buffer = cv2.imencode('.png', deskewed_image)
            pil_image = Image.open(io.BytesIO(buffer))

            return pil_image, skew_angle

        except Exception as e:
            logger.error(f"Deskew error: {e}")
            # Возвращаем оригинальное изображение в случае ошибки
            pix = pdf_page.get_pixmap()
            img_data = pix.tobytes("png")
            return Image.open(io.BytesIO(img_data)), 0