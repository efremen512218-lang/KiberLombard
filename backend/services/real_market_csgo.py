"""
PRODUCTION интеграция с market.csgo.com
Реальные HTTP запросы без fallback на демо данные
"""
import httpx
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
import os


class RealMarketCSGOService:
    """Production сервис для market.csgo с реальными запросами"""
    
    API_URL = "https://market.csgo.com/api/v2"
    API_KEY = os.getenv("MARKET_CSGO_API_KEY", "")
    
    # Кеш
    _price_cache: Dict[str, tuple[float, datetime]] = {}
    _all_prices_cache: tuple[Dict[str, dict], datetime] = ({}, datetime.min)
    _cache_ttl = timedelta(hours=1)
    
    @staticmethod
    async def get_all_prices() -> Dict[str, dict]:
        """
        Получить ВСЕ цены одним запросом (эффективно)
        
        Returns:
            Dict[market_hash_name, {price, avg_price, popularity}]
        """
        # Проверяем кеш всех цен
        cached_prices, cached_time = RealMarketCSGOService._all_prices_cache
        if datetime.now() - cached_time < RealMarketCSGOService._cache_ttl:
            print(f"[MARKET.CSGO] Используем кеш ({len(cached_prices)} предметов)")
            return cached_prices
        
        print("[MARKET.CSGO] Загружаем ВСЕ цены...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{RealMarketCSGOService.API_URL}/prices/RUB.json",
                    headers={"User-Agent": "CyberLombard/1.0"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if not data.get("success"):
                        print("[MARKET.CSGO] API вернул success=false")
                        return {}
                    
                    items = data.get("items", {})
                    print(f"[MARKET.CSGO] Получено {len(items)} цен")
                    
                    # Кешируем
                    RealMarketCSGOService._all_prices_cache = (items, datetime.now())
                    
                    return items
                else:
                    print(f"[MARKET.CSGO] HTTP {response.status_code}")
                    return {}
        
        except httpx.TimeoutException:
            print("[MARKET.CSGO] Timeout")
            return {}
        except Exception as e:
            print(f"[MARKET.CSGO] Ошибка: {e}")
            return {}
    
    @staticmethod
    async def get_prices(market_hash_names: List[str]) -> Dict[str, float]:
        """
        Получить цены для списка предметов
        
        Args:
            market_hash_names: Список названий
            
        Returns:
            Dict[market_hash_name, price_rub]
        """
        # Получаем все цены
        all_prices = await RealMarketCSGOService.get_all_prices()
        
        if not all_prices:
            print("[MARKET.CSGO] Не удалось получить цены")
            return {name: 0.0 for name in market_hash_names}
        
        # Извлекаем нужные
        result = {}
        for name in market_hash_names:
            if name in all_prices:
                item_data = all_prices[name]
                # Используем минимальную цену (instant sell)
                price = float(item_data.get("price", 0))
                result[name] = price
            else:
                result[name] = 0.0
        
        found = len([p for p in result.values() if p > 0])
        print(f"[MARKET.CSGO] Найдено {found}/{len(market_hash_names)} цен")
        
        return result
    
    @staticmethod
    async def get_item_details(market_hash_names: List[str]) -> Dict[str, dict]:
        """
        Получить детальную информацию (требует API ключ)
        
        Args:
            market_hash_names: Список названий
            
        Returns:
            Dict[market_hash_name, details]
        """
        if not RealMarketCSGOService.API_KEY:
            print("[MARKET.CSGO] API ключ не установлен")
            return {}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Формируем параметры
                params = {"key": RealMarketCSGOService.API_KEY}
                for name in market_hash_names:
                    params["list_hash_name[]"] = name
                
                response = await client.get(
                    f"{RealMarketCSGOService.API_URL}/get-list-items-info",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {})
                else:
                    print(f"[MARKET.CSGO] Детали: HTTP {response.status_code}")
                    return {}
        
        except Exception as e:
            print(f"[MARKET.CSGO] Ошибка деталей: {e}")
            return {}
    
    @staticmethod
    def clear_cache():
        """Очистить весь кеш"""
        RealMarketCSGOService._price_cache.clear()
        RealMarketCSGOService._all_prices_cache = ({}, datetime.min)
        print("[MARKET.CSGO] Кеш очищен")
