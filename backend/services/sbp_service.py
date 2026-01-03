"""
Сервис выплат через СБП
"""
import httpx
from typing import Dict, Optional
from datetime import datetime
from config import get_settings


class SBPService:
    """Сервис для выплат через Систему Быстрых Платежей"""
    
    @staticmethod
    async def create_payout(
        phone: str,
        amount: float,
        deal_id: int,
        description: str = ""
    ) -> str:
        """
        Создать выплату
        
        Args:
            phone: Номер телефона получателя
            amount: Сумма выплаты
            deal_id: ID сделки
            description: Описание платежа
            
        Returns:
            payout_id
        """
        settings = get_settings()
        
        # Проверка лимитов
        if amount < settings.sbp_min_amount:
            raise ValueError(f"Сумма меньше минимальной ({settings.sbp_min_amount})")
        if amount > settings.sbp_max_amount:
            raise ValueError(f"Сумма больше максимальной ({settings.sbp_max_amount})")
        
        payout_id = f"sbp_{deal_id}_{int(datetime.now().timestamp())}"
        
        if settings.sbp_provider == "fake":
            # Фейковый провайдер
            print(f"[SBP] FAKE: Создана выплата {payout_id} на {phone} сумма {amount}")
            return payout_id
        elif settings.sbp_provider == "modulbank":
            return await SBPService._create_modulbank(phone, amount, description, settings.sbp_api_key)
        else:
            raise ValueError(f"Unknown SBP provider: {settings.sbp_provider}")
    
    @staticmethod
    async def check_status(payout_id: str) -> str:
        """
        Проверить статус выплаты
        
        Returns:
            "pending" | "processing" | "completed" | "failed"
        """
        settings = get_settings()
        
        if settings.sbp_provider == "fake":
            # Фейковый провайдер - всегда completed
            return "completed"
        elif settings.sbp_provider == "modulbank":
            return await SBPService._check_status_modulbank(payout_id, settings.sbp_api_key)
        else:
            return "failed"
    
    @staticmethod
    async def _create_modulbank(phone: str, amount: float, description: str, api_key: str) -> str:
        """Создать выплату через Modulbank"""
        url = "https://api.modulbank.ru/v1/sbp-payout"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "phone": phone,
            "amount": amount,
            "description": description
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    payout_id = result.get("id")
                    print(f"[MODULBANK] Создана выплата: {payout_id}")
                    return payout_id
                else:
                    print(f"[MODULBANK] Ошибка: {response.status_code}")
                    raise Exception("Failed to create payout")
                    
        except Exception as e:
            print(f"[MODULBANK] Исключение: {e}")
            raise
    
    @staticmethod
    async def _check_status_modulbank(payout_id: str, api_key: str) -> str:
        """Проверить статус в Modulbank"""
        url = f"https://api.modulbank.ru/v1/sbp-payout/{payout_id}"
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    
                    # Маппинг статусов
                    status_map = {
                        "new": "pending",
                        "processing": "processing",
                        "success": "completed",
                        "failed": "failed",
                        "cancelled": "failed"
                    }
                    
                    return status_map.get(status, "pending")
                else:
                    return "pending"
                    
        except Exception as e:
            print(f"[MODULBANK] Ошибка получения статуса: {e}")
            return "pending"
