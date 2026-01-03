"""
Валидаторы для входных данных
"""
import re
from typing import Optional


def validate_steam_id(steam_id: str) -> bool:
    """Проверить формат Steam ID (64-bit)"""
    if not steam_id:
        return False
    return steam_id.isdigit() and len(steam_id) == 17


def validate_phone(phone: str) -> bool:
    """Проверить формат телефона РФ"""
    pattern = r'^\+7\d{10}$'
    return bool(re.match(pattern, phone))


def validate_asset_id(asset_id: str) -> bool:
    """Проверить формат asset ID"""
    return asset_id.isdigit() and len(asset_id) > 0


def validate_option_days(days: int) -> bool:
    """Проверить срок опциона"""
    return 7 <= days <= 30


def validate_amount(amount: float) -> bool:
    """Проверить сумму"""
    return amount > 0 and amount < 10_000_000  # Макс 10 млн


def validate_passport_series(series: str) -> bool:
    """Проверить серию паспорта"""
    return series.isdigit() and len(series) == 4


def validate_passport_number(number: str) -> bool:
    """Проверить номер паспорта"""
    return number.isdigit() and len(number) == 6


def validate_sms_code(code: str) -> bool:
    """Проверить SMS код"""
    return code.isdigit() and len(code) == 6


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """Очистить строку от опасных символов"""
    if not text:
        return ""
    # Убрать HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    # Ограничить длину
    return text[:max_length].strip()
