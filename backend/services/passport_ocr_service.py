"""
Сервис распознавания паспорта РФ через OCR
Использует pytesseract (Tesseract OCR) для локального распознавания
Улучшенная версия с продвинутой предобработкой изображения
"""
import re
import base64
from typing import Optional, Dict, List, Tuple
from io import BytesIO
from dataclasses import dataclass

# Попробуем импортировать зависимости
try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    import pytesseract
    
    # Путь к Tesseract на Windows
    import os
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe',
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
    
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("[OCR] Установите: pip install pytesseract pillow")


@dataclass
class PassportData:
    """Данные паспорта"""
    full_name: str = ""
    surname: str = ""
    name: str = ""
    patronymic: str = ""
    series: str = ""
    number: str = ""
    birth_date: str = ""
    birth_place: str = ""
    issued_by: str = ""
    issue_date: str = ""
    department_code: str = ""
    gender: str = ""
    raw_text: str = ""
    confidence: float = 0.0


class PassportOCRService:
    """Сервис распознавания паспорта РФ"""
    
    # Слова которые нужно игнорировать при поиске ФИО
    IGNORE_WORDS = {
        'РОССИЙСКАЯ', 'ФЕДЕРАЦИЯ', 'ПАСПОРТ', 'ГРАЖДАНИНА', 'PASSPORT',
        'ВЫДАН', 'ОТДЕЛОМ', 'ОТДЕЛЕНИЕМ', 'УПРАВЛЕНИЯ', 'УПРАВЛЕНИЕМ',
        'МЕСТО', 'РОЖДЕНИЯ', 'ДАТА', 'ПОЛ', 'МУЖ', 'ЖЕН',
        'ГОРОДА', 'ОБЛАСТИ', 'РАЙОНА', 'ОКРУГА', 'КРАЯ',
        'ОКТЯБРЬСКОГО', 'ЛЕНИНСКОГО', 'КИРОВСКОГО', 'СОВЕТСКОГО',
        'ВНУТРЕННИХ', 'ДЕЛ', 'ПО', 'ГОР', 'ОБЛ', 'КОД', 'ПОДРАЗДЕЛЕНИЯ',
        'АРХАНГЕЛЬСК', 'АРХАНГЕЛЬСКА', 'АРХАНГЕЛЬСКОЙ',
        'МОСКВА', 'МОСКВЫ', 'МОСКОВСКОЙ', 'САНКТ', 'ПЕТЕРБУРГ',
    }
    
    @classmethod
    def extract_from_base64(cls, base64_image: str) -> PassportData:
        """Извлечь данные паспорта из base64 изображения"""
        if not OCR_AVAILABLE:
            return PassportData(raw_text="OCR не доступен")
        
        try:
            # Убираем data:image/... префикс
            if ',' in base64_image:
                base64_image = base64_image.split(',')[1]
            
            image_data = base64.b64decode(base64_image)
            image = Image.open(BytesIO(image_data))
            
            print(f"[OCR] Размер изображения: {image.size}")
            
            # Пробуем несколько вариантов предобработки
            all_texts = []
            
            # Вариант 1: Стандартная обработка
            img1 = cls._preprocess_standard(image.copy())
            text1 = cls._ocr_image(img1)
            all_texts.append(text1)
            
            # Вариант 2: Высокий контраст
            img2 = cls._preprocess_high_contrast(image.copy())
            text2 = cls._ocr_image(img2)
            all_texts.append(text2)
            
            # Вариант 3: Бинаризация (черно-белое)
            img3 = cls._preprocess_binary(image.copy())
            text3 = cls._ocr_image(img3)
            all_texts.append(text3)
            
            # Объединяем все тексты для лучшего парсинга
            combined_text = '\n'.join(all_texts)
            
            print(f"[OCR] Распознано символов: {len(combined_text)}")
            
            # Парсим данные
            return cls._parse_passport_text(combined_text, all_texts)
            
        except Exception as e:
            print(f"[OCR] Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return PassportData(raw_text=f"Ошибка: {str(e)}")
    
    @classmethod
    def _ocr_image(cls, image: Image.Image) -> str:
        """Распознать текст с изображения"""
        try:
            # Пробуем русский язык
            text = pytesseract.image_to_string(
                image,
                lang='rus',
                config='--psm 6 --oem 3 -c preserve_interword_spaces=1'
            )
            return text
        except:
            try:
                # Fallback на английский
                return pytesseract.image_to_string(image, lang='eng', config='--psm 6')
            except:
                return ""
    
    @classmethod
    def _preprocess_standard(cls, image: Image.Image) -> Image.Image:
        """Стандартная предобработка"""
        # RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Масштабируем до оптимального размера
        width, height = image.size
        if width < 2000:
            scale = 2000 / width
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Grayscale
        image = image.convert('L')
        
        # Контраст
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Резкость
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        return image
    
    @classmethod
    def _preprocess_high_contrast(cls, image: Image.Image) -> Image.Image:
        """Высококонтрастная обработка"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Масштаб
        width, height = image.size
        if width < 2500:
            scale = 2500 / width
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Grayscale
        image = image.convert('L')
        
        # Автоконтраст
        image = ImageOps.autocontrast(image, cutoff=2)
        
        # Сильный контраст
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.5)
        
        # Резкость
        image = image.filter(ImageFilter.SHARPEN)
        image = image.filter(ImageFilter.SHARPEN)
        
        return image
    
    @classmethod
    def _preprocess_binary(cls, image: Image.Image) -> Image.Image:
        """Бинаризация - черно-белое изображение"""
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Масштаб
        width, height = image.size
        if width < 2000:
            scale = 2000 / width
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Grayscale
        image = image.convert('L')
        
        # Автоконтраст
        image = ImageOps.autocontrast(image, cutoff=5)
        
        # Бинаризация (порог)
        threshold = 140
        image = image.point(lambda x: 255 if x > threshold else 0, '1')
        
        return image
    
    @classmethod
    def _parse_passport_text(cls, combined_text: str, all_texts: List[str]) -> PassportData:
        """Парсинг текста паспорта"""
        data = PassportData(raw_text=combined_text[:1000])
        
        # Нормализуем текст
        text_upper = combined_text.upper()
        
        # === 1. Серия и номер паспорта ===
        # Ищем паттерн: 2 цифры, 2 цифры, 6 цифр
        series_patterns = [
            r'(\d{2})\s*(\d{2})\s+(\d{6})',  # 29 20 000000
            r'(\d{2})\s*(\d{2})\s*№?\s*(\d{6})',  # 2920 №000000
            r'(\d{4})\s+(\d{6})',  # 2920 000000
        ]
        
        for pattern in series_patterns:
            match = re.search(pattern, combined_text)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    data.series = f"{groups[0]} {groups[1]}"
                    data.number = groups[2]
                elif len(groups) == 2:
                    data.series = f"{groups[0][:2]} {groups[0][2:]}"
                    data.number = groups[1]
                data.confidence += 0.25
                print(f"[OCR] Найдена серия/номер: {data.series} {data.number}")
                break
        
        # === 2. Код подразделения ===
        code_match = re.search(r'(\d{3})[-\s](\d{3})', combined_text)
        if code_match:
            data.department_code = f"{code_match.group(1)}-{code_match.group(2)}"
            data.confidence += 0.15
            print(f"[OCR] Найден код подразделения: {data.department_code}")
        
        # === 3. Даты ===
        date_pattern = r'(\d{2})[.\s/](\d{2})[.\s/](\d{4})'
        all_dates = re.findall(date_pattern, combined_text)
        
        valid_dates = []
        for d, m, y in all_dates:
            day, month, year = int(d), int(m), int(y)
            # Валидация даты
            if 1 <= day <= 31 and 1 <= month <= 12 and 1940 <= year <= 2025:
                valid_dates.append(f"{d}.{m}.{y}")
        
        # Убираем дубликаты, сохраняя порядок
        seen = set()
        unique_dates = []
        for d in valid_dates:
            if d not in seen:
                seen.add(d)
                unique_dates.append(d)
        
        if unique_dates:
            # Сортируем по году - первая дата обычно дата рождения
            sorted_dates = sorted(unique_dates, key=lambda x: int(x.split('.')[-1]))
            
            data.birth_date = sorted_dates[0]
            data.confidence += 0.15
            print(f"[OCR] Найдена дата рождения: {data.birth_date}")
            
            if len(sorted_dates) > 1:
                data.issue_date = sorted_dates[-1]  # Последняя - дата выдачи
                data.confidence += 0.1
                print(f"[OCR] Найдена дата выдачи: {data.issue_date}")
        
        # === 4. ФИО ===
        # Ищем слова на кириллице с заглавной буквы
        fio_candidates = cls._extract_fio_candidates(combined_text)
        
        if fio_candidates:
            # Берём первые 3 подходящих слова
            if len(fio_candidates) >= 3:
                data.surname = fio_candidates[0]
                data.name = fio_candidates[1]
                data.patronymic = fio_candidates[2]
                data.full_name = f"{data.surname} {data.name} {data.patronymic}"
                data.confidence += 0.25
                print(f"[OCR] Найдено ФИО: {data.full_name}")
            elif len(fio_candidates) >= 2:
                data.surname = fio_candidates[0]
                data.name = fio_candidates[1]
                data.full_name = f"{data.surname} {data.name}"
                data.confidence += 0.15
        
        # === 5. Пол ===
        if 'МУЖ' in text_upper:
            data.gender = 'М'
            data.confidence += 0.05
        elif 'ЖЕН' in text_upper:
            data.gender = 'Ж'
            data.confidence += 0.05
        
        # === 6. Место рождения ===
        # Ищем после "МЕСТО РОЖДЕНИЯ" или "ГОР."
        birth_place_match = re.search(
            r'(?:МЕСТО\s*РОЖДЕНИЯ|ГОР\.?|Г\.)\s*([А-ЯЁа-яё\s]+)',
            text_upper
        )
        if birth_place_match:
            place = birth_place_match.group(1).strip()
            # Берём первое слово (город)
            words = place.split()
            if words:
                data.birth_place = words[0].capitalize()
                data.confidence += 0.05
        
        return data
    
    @classmethod
    def _extract_fio_candidates(cls, text: str) -> List[str]:
        """Извлечь кандидатов на ФИО"""
        # Ищем слова на кириллице
        words = re.findall(r'[А-ЯЁ][а-яё]{2,}', text)
        
        candidates = []
        for word in words:
            word_upper = word.upper()
            # Пропускаем служебные слова
            if word_upper in cls.IGNORE_WORDS:
                continue
            # Пропускаем слишком короткие или длинные
            if len(word) < 3 or len(word) > 20:
                continue
            # Пропускаем слова с цифрами
            if any(c.isdigit() for c in word):
                continue
            
            candidates.append(word.capitalize())
        
        # Убираем дубликаты
        seen = set()
        unique = []
        for c in candidates:
            if c.upper() not in seen:
                seen.add(c.upper())
                unique.append(c)
        
        return unique[:5]  # Возвращаем первые 5 кандидатов
    
    @classmethod
    def to_dict(cls, data: PassportData) -> Dict:
        """Конвертировать в словарь для API"""
        return {
            "full_name": data.full_name,
            "surname": data.surname,
            "name": data.name,
            "patronymic": data.patronymic,
            "series": data.series,
            "number": data.number,
            "birth_date": data.birth_date,
            "birth_place": data.birth_place,
            "issued_by": data.issued_by,
            "issue_date": data.issue_date,
            "department_code": data.department_code,
            "gender": data.gender,
            "confidence": round(data.confidence, 2),
            "raw_text": data.raw_text[:500] if data.raw_text else ""
        }


if __name__ == "__main__":
    if OCR_AVAILABLE:
        print("✓ OCR доступен")
        print(f"  Tesseract: {pytesseract.get_tesseract_version()}")
    else:
        print("✗ OCR не доступен")
