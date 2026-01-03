import re
import urllib.parse
from typing import Optional, Dict
import httpx

class SteamAuthService:
    """Сервис для Steam OpenID авторизации"""
    
    STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
    
    @staticmethod
    def get_login_url(return_url: str) -> str:
        """
        Генерация URL для редиректа на Steam авторизацию
        
        Args:
            return_url: URL для возврата после авторизации
        
        Returns:
            URL для редиректа
        """
        params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": return_url,
            "openid.realm": return_url.rsplit('/', 1)[0],
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"{SteamAuthService.STEAM_OPENID_URL}?{query_string}"
    
    @staticmethod
    async def verify_openid_response(params: Dict[str, str]) -> Optional[str]:
        """
        Верификация ответа от Steam OpenID
        
        Args:
            params: Query параметры из callback URL
        
        Returns:
            Steam ID64 или None если верификация не прошла
        """
        # Проверка наличия обязательных параметров
        if "openid.claimed_id" not in params:
            return None
        
        # Извлечение Steam ID из claimed_id
        claimed_id = params["openid.claimed_id"]
        steam_id_match = re.search(r"https://steamcommunity.com/openid/id/(\d+)", claimed_id)
        
        if not steam_id_match:
            return None
        
        steam_id = steam_id_match.group(1)
        
        # Верификация подписи через Steam
        verification_params = dict(params)
        verification_params["openid.mode"] = "check_authentication"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    SteamAuthService.STEAM_OPENID_URL,
                    data=verification_params
                )
                
                response_text = response.text
                
                if "is_valid:true" in response_text:
                    return steam_id
                else:
                    print(f"[STEAM AUTH] Верификация не прошла: {response_text}")
                    return None
                    
            except Exception as e:
                print(f"[STEAM AUTH] Ошибка верификации: {e}")
                return None
    
    @staticmethod
    def extract_steam_id_from_url(url: str) -> Optional[str]:
        """
        Извлечь Steam ID из различных форматов URL
        
        Поддерживаемые форматы:
        - Trade offer: https://steamcommunity.com/tradeoffer/new/?partner=346262790&token=xxx
        - Profile: https://steamcommunity.com/profiles/76561198306528518
        - Steam ID: 76561198306528518
        """
        # Trade offer partner ID
        if "partner=" in url:
            match = re.search(r"partner=(\d+)", url)
            if match:
                partner_id = int(match.group(1))
                # Конвертация partner ID в Steam ID64
                steam_id64 = 76561197960265728 + partner_id
                return str(steam_id64)
        
        # Profile URL
        if "profiles/" in url:
            match = re.search(r"profiles/(\d+)", url)
            if match:
                return match.group(1)
        
        # Просто Steam ID
        if re.match(r"^\d{17}$", url):
            return url
        
        return None
    
    @staticmethod
    def parse_trade_url(trade_url: str) -> Optional[dict]:
        """
        Парсинг trade URL для получения partner ID и token
        
        Args:
            trade_url: Trade URL вида https://steamcommunity.com/tradeoffer/new/?partner=346262790&token=84ThNh2-
        
        Returns:
            Dict с steam_id64 и trade_token или None
        """
        if not trade_url or "partner=" not in trade_url:
            return None
        
        try:
            # Извлекаем partner ID
            partner_match = re.search(r"partner=(\d+)", trade_url)
            if not partner_match:
                return None
            
            partner_id = int(partner_match.group(1))
            steam_id64 = 76561197960265728 + partner_id
            
            # Извлекаем token
            token_match = re.search(r"token=([a-zA-Z0-9_-]+)", trade_url)
            trade_token = token_match.group(1) if token_match else None
            
            return {
                "steam_id64": str(steam_id64),
                "trade_token": trade_token,
                "partner_id": partner_id
            }
        except Exception as e:
            print(f"[TRADE_URL] Ошибка парсинга: {e}")
            return None
