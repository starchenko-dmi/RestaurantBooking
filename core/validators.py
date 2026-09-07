from django.core.exceptions import ValidationError

from PIL import Image


def validate_image_file_size(image):
    """Проверка размера изображения (макс 2MB)"""
    filesize = image.size
    max_size = 2 * 1024 * 1024  # 2MB
    if filesize > max_size:
        raise ValidationError(f"Максимальный размер файла 2MB. Ваш файл: {filesize / 1024 / 1024:.2f}MB")


def validate_image_dimensions(image, min_width=1600, min_height=600):
    """Проверка минимальных размеров изображения"""
    try:
        img = Image.open(image)
        width, height = img.size

        if width < min_width:
            raise ValidationError(
                f"Минимальная ширина изображения {min_width}px. Ваша: {width}px. " f"Рекомендуемый размер: 1920x800px"
            )

        if height < min_height:
            raise ValidationError(
                f"Минимальная высота изображения {min_height}px. Ваша: {height}px. " f"Рекомендуемый размер: 1920x800px"
            )
    except Exception:
        # Если не удалось открыть как изображение
        pass
