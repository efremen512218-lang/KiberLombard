"""
Сервис отправки SMS с поддержкой разных провайдеров
"""
import httpx
import hashlib
import secrets
from typing import Optional
from datetime import datetime, timedelta
from config import get_settings


class SMSService:
    """Сервис для отправки SMS кодов"""
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Генерировать случайный код"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @staticmethod
    def hash_code(code: str) -> str:
        """Хешировать код для хранения"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    @staticmethod
    def check_hash(code: str, hashed: str) -> bool:
        """Проверить код по хешу"""
        return SMSService.hash_code(code) == hashed
    
    @staticmethod
    async def send_verification_code(phone: str, purpose: str = "verification") -> str:
        """
        Отправить SMS код
        
        Args:
            phone: Номер телефона (+7XXXXXXXXXX)
            purpose: Цель отправки (verification, deal_sign, etc.)
            
        Returns:
            code - код (только для dev!)
        """
        settings = get_settings()
        
        # Генерируем код
        code = SMSService.generate_code(settings.sms_code_length)
        
        # Текст сообщения
        messages = {
            "verification": f"Код подтверждения КиберЛомбард: {code}",
            "deal_sign": f"Код подписи договора КиберЛомбард: {code}",
            "buyback": f"Код выкупа КиберЛомбард: {code}"
        }
        text = messages.get(purpose, f"Ваш код: {code}")
        
        # Отправляем через провайдера
        if settings.sms_provider == "fake":
            # Фейковый провайдер для разработки
            print(f"[SMS] FAKE: {phone} -> {code}")
            success = True
        elif settings.sms_provider == "sms.ru":
            success = await SMSService._send_sms_ru(phone, text, settings.sms_api_key)
        elif settings.sms_provider == "smsc.ru":
            success = await SMSService._send_smsc(phone, text, settings.sms_api_key)
        else:
            raise ValueError(f"Unknown SMS provider: {settings.sms_provider}")
        
        if not success:
            raise Exception("Failed to send SMS")
        
        # Возвращаем код (в проде не возвращать!)
        return code
    
    @staticmethod
    async def _send_sms_ru(phone: str, text: str, api_key: str) -> bool:
        """Отправить через SMS.ru"""
        url = "https://sms.ru/sms/send"
        
        params = {
            "api_id": api_key,
            "to": phone,
            "msg": text,
            "json": 1
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
                
                if data.get("status") == "OK":
                    print(f"[SMS.RU] Отправлено: {phone}")
                    return True
                else:
                    print(f"[SMS.RU] Ошибка: {data}")
                    return False
                    
        except Exception as e:
            print(f"[SMS.RU] Исключение: {e}")
            return False
    
    @staticmethod
    async def _send_smsc(phone: str, text: str, api_key: str) -> bool:
        """Отправить через SMSC.ru"""
        url = "https://smsc.ru/sys/send.php"
        
        params = {
            "login": "your_login",  # Из конфига
            "psw": api_key,
            "phones": phone,
            "mes": text,
            "fmt": 3  # JSON
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
                
                if data.get("error_code") is None:
                    print(f"[SMSC] Отправлено: {phone}")
                    return True
                else:
                    print(f"[SMSC] Ошибка: {data}")
                    return False
                    
        except Exception as e:
            print(f"[SMSC] Исключение: {e}")
            return False
