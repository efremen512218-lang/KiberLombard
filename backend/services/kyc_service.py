"""
Сервис KYC проверки паспортов
"""
import httpx
import asyncio
from typing import Dict, Optional
from datetime import datetime
from config import get_settings


class KYCService:
    """Сервис для проверки паспортных данных"""
    
    @staticmethod
    async def submit_verification(user_id: int, data: Dict) -> str:
        """
        Отправить данные на проверку
        
        Args:
            user_id: ID пользователя
            data: Паспортные данные
            
        Returns:
            verification_id
        """
        settings = get_settings()
        
        verification_id = f"kyc_{user_id}_{int(datetime.now().timestamp())}"
        
        if settings.kyc_provider == "fake":
            # Фейковый провайдер - автоматически одобряем через 2 секунды
            print(f"[KYC] FAKE: Создана проверка {verification_id}")
            asyncio.create_task(KYCService._fake_approve(verification_id))
            return verification_id
        elif settings.kyc_provider == "sumsub":
            return await KYCService._submit_sumsub(user_id, data, settings.kyc_api_key)
        else:
            raise ValueError(f"Unknown KYC provider: {settings.kyc_provider}")
    
    @staticmethod
    async def get_status(verification_id: str) -> str:
        """
        Получить статус проверки
        
        Returns:
            "pending" | "passed" | "failed"
        """
        settings = get_settings()
        
        if settings.kyc_provider == "fake":
            # Фейковый провайдер - всегда passed после задержки
            return "passed"
        elif settings.kyc_provider == "sumsub":
            return await KYCService._get_status_sumsub(verification_id, settings.kyc_api_key)
        else:
            return "failed"
    
    @staticmethod
    async def _fake_approve(verification_id: str):
        """Фейковое одобрение через 2 секунды"""
        await asyncio.sleep(2)
        print(f"[KYC] FAKE: Проверка {verification_id} одобрена")
    
    @staticmethod
    async def _submit_sumsub(user_id: int, data: Dict, api_key: str) -> str:
        """Отправить в Sumsub"""
        url = "https://api.sumsub.com/resources/applicants"
        
        headers = {
            "X-App-Token": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "externalUserId": str(user_id),
            "info": {
                "firstName": data["first_name"],
                "lastName": data["last_name"],
                "middleName": data.get("middle_name", ""),
                "dob": data["birth_date"],
                "idDocs": [{
                    "idDocType": "ID_CARD",
                    "country": "RUS",
                    "number": f"{data['passport_series']}{data['passport_number']}",
                    "issuedDate": data["issue_date"]
                }]
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 201:
                    result = response.json()
                    verification_id = result.get("id")
                    print(f"[SUMSUB] Создана проверка: {verification_id}")
                    return verification_id
                else:
                    print(f"[SUMSUB] Ошибка: {response.status_code}")
                    raise Exception("Failed to create verification")
                    
        except Exception as e:
            print(f"[SUMSUB] Исключение: {e}")
            raise
    
    @staticmethod
    async def _get_status_sumsub(verification_id: str, api_key: str) -> str:
        """Получить статус из Sumsub"""
        url = f"https://api.sumsub.com/resources/applicants/{verification_id}/status"
        
        headers = {
            "X-App-Token": api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    review_status = result.get("reviewStatus")
                    
                    # Маппинг статусов Sumsub
                    status_map = {
                        "init": "pending",
                        "pending": "pending",
                        "prechecked": "pending",
                        "queued": "pending",
                        "completed": "passed",
                        "onHold": "pending",
                        "rejected": "failed"
                    }
                    
                    return status_map.get(review_status, "pending")
                else:
                    return "pending"
                    
        except Exception as e:
            print(f"[SUMSUB] Ошибка получения статуса: {e}")
            return "pending"
