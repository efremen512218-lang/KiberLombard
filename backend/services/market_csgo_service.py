"""
Интеграция с market.csgo.com для получения instant цен
ОПТИМИЗИРОВАНО: Загружаем весь прайс-лист один раз и кэшируем
"""
import httpx
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class MarketCSGOService:
    """Сервис для получения цен с market.csgo.com"""
    
    API_URL = "https://market.csgo.com/api/v2"
    
    # Глобальный кэш всех цен (загружается один раз)
    _all_prices: Dict[str, float] = {}
    _all_prices_loaded_at: Optional[datetime] = None
    _cache_ttl = timedelta(hours=1)
    
    @staticmethod
    async def get_prices(market_hash_names: List[str]) -> Dict[str, float]:
        """
        Получить instant цены с market.csgo
        
        Returns:
            Dict[market_hash_name, price_rub]
        """
        # Загружаем все цены если кэш пустой или устарел
        await MarketCSGOService._ensure_prices_loaded()
        
        # Быстро достаём нужные цены из кэша
        prices = {}
        for name in market_hash_names:
            price = MarketCSGOService._all_prices.get(name, 0.0)
            prices[name] = price
        
        successful = len([p for p in prices.values() if p > 0])
        print(f"[MARKET.CSGO] Найдено {successful}/{len(market_hash_names)} цен в кэше")
        
        return prices
    
    @staticmethod
    async def _ensure_prices_loaded():
        """Загрузить все цены если нужно"""
        now = datetime.now()
        
        # Проверяем нужно ли обновить кэш
        if (MarketCSGOService._all_prices_loaded_at is None or 
            now - MarketCSGOService._all_prices_loaded_at > MarketCSGOService._cache_ttl):
            
            print("[MARKET.CSGO] Загружаем прайс-лист...")
            await MarketCSGOService._load_all_prices()
    
    @staticmethod
    async def _load_all_prices():
        """Загрузить весь прайс-лист с API"""
        url = f"{MarketCSGOService.API_URL}/prices/RUB.json"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Формат: {"items": [{"market_hash_name": "...", "price": 123}]}
                    items = data.get("items", [])
                    
                    # Очищаем старый кэш
                    MarketCSGOService._all_prices.clear()
                    
                    # Загружаем все цены
                    for item in items:
                        market_name = item.get("market_hash_name")
                        price = float(item.get("price", 0))
                        if market_name and price > 0:
                            MarketCSGOService._all_prices[market_name] = price
                    
                    MarketCSGOService._all_prices_loaded_at = datetime.now()
                    print(f"[MARKET.CSGO] ✅ Загружено {len(MarketCSGOService._all_prices)} цен")
                    
                else:
                    print(f"[MARKET.CSGO] ❌ Ошибка {response.status_code}")
                    
        except Exception as e:
            print(f"[MARKET.CSGO] ❌ Ошибка загрузки: {e}")
    
    @staticmethod
    def get_cached_price(name: str) -> float:
        """Получить цену из кэша (синхронно)"""
        return MarketCSGOService._all_prices.get(name, 0.0)
    
    @staticmethod
    def clear_cache():
        """Очистить кэш"""
        MarketCSGOService._all_prices.clear()
        MarketCSGOService._all_prices_loaded_at = None
        print("[MARKET.CSGO] Кэш очищен")
    
    @staticmethod
    def get_cache_stats() -> dict:
        """Статистика кэша"""
        return {
            "items_count": len(MarketCSGOService._all_prices),
            "loaded_at": MarketCSGOService._all_prices_loaded_at.isoformat() if MarketCSGOService._all_prices_loaded_at else None,
            "is_stale": MarketCSGOService._all_prices_loaded_at is None or 
                        datetime.now() - MarketCSGOService._all_prices_loaded_at > MarketCSGOService._cache_ttl
        }
