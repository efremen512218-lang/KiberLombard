import httpx
import uuid
from typing import Dict, Optional
from config import get_settings
from datetime import datetime

settings = get_settings()

class PaymentService:
    """Сервис для работы с платежами через ЮKassa"""
    
    BASE_URL = "https://api.yookassa.ru/v3"
    
    @staticmethod
    async def create_payout(
        phone: str,
        amount: float,
        description: str,
        deal_id: int
    ) -> Optional[str]:
        """
        Создать выплату клиенту через СБП/ЮKassa
        
        Args:
            phone: Номер телефона получателя
            amount: Сумма выплаты
            description: Описание платежа
            deal_id: ID сделки
        
        Returns:
            ID транзакции или None при ошибке
        """
        if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
            print(f"[PAYMENT] DEV MODE: Выплата {amount}₽ на {phone} (сделка #{deal_id})")
            return f"dev_payout_{uuid.uuid4().hex[:8]}"
        
        # Реальная интеграция с ЮKassa
        url = f"{PaymentService.BASE_URL}/payouts"
        
        payload = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "payout_destination_data": {
                "type": "sbp",
                "phone": phone
            },
            "description": description,
            "metadata": {
                "deal_id": deal_id
            }
        }
        
        headers = {
            "Idempotence-Key": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }
        
        auth = (settings.yookassa_shop_id, settings.yookassa_secret_key)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    auth=auth
                )
                response.raise_for_status()
                data = response.json()
                
                payout_id = data.get("id")
                print(f"[PAYMENT] Выплата создана: {payout_id}")
                
                return payout_id
                
            except Exception as e:
                print(f"[PAYMENT] Ошибка создания выплаты: {e}")
                return None
    
    @staticmethod
    async def create_payment(
        amount: float,
        description: str,
        return_url: str,
        deal_id: int
    ) -> Optional[Dict]:
        """
        Создать платеж для выкупа (клиент платит нам)
        
        Returns:
            Dict с payment_id и confirmation_url
        """
        if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
            print(f"[PAYMENT] DEV MODE: Платеж {amount}₽ (сделка #{deal_id})")
            return {
                "payment_id": f"dev_payment_{uuid.uuid4().hex[:8]}",
                "confirmation_url": f"{return_url}?payment=success",
                "status": "pending"
            }
        
        url = f"{PaymentService.BASE_URL}/payments"
        
        payload = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
            "metadata": {
                "deal_id": deal_id
            }
        }
        
        headers = {
            "Idempotence-Key": str(uuid.uuid4()),
            "Content-Type": "application/json"
        }
        
        auth = (settings.yookassa_shop_id, settings.yookassa_secret_key)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    auth=auth
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "payment_id": data.get("id"),
                    "confirmation_url": data["confirmation"]["confirmation_url"],
                    "status": data.get("status")
                }
                
            except Exception as e:
                print(f"[PAYMENT] Ошибка создания платежа: {e}")
                return None
    
    @staticmethod
    async def check_payment_status(payment_id: str) -> Optional[str]:
        """
        Проверить статус платежа
        
        Returns:
            "pending", "succeeded", "canceled" или None
        """
        if payment_id.startswith("dev_"):
            return "succeeded"  # DEV mode
        
        if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
            return "succeeded"
        
        url = f"{PaymentService.BASE_URL}/payments/{payment_id}"
        auth = (settings.yookassa_shop_id, settings.yookassa_secret_key)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, auth=auth)
                response.raise_for_status()
                data = response.json()
                
                return data.get("status")
                
            except Exception as e:
                print(f"[PAYMENT] Ошибка проверки статуса: {e}")
                return None
