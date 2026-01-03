"""
Получение реальных цен через SteamAPIs.com
Бесплатно: 10,000 запросов/день
Регистрация: https://steamapis.com/
"""
import httpx
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta


class SteamAPIsPriceService:
    """
    Профессиональный сервис цен через SteamAPIs.com
    
    Преимущества:
    - Реальные цены Steam Market
    - Быстрый ответ (кешированные данные)
    - Без rate limiting (10k запросов/день)
    - Бесплатный тарифный план
    """
    
    # API ключ (получить на https://steamapis.com/)
    # Для демо используем публичный endpoint (ограниченный)
    API_KEY = None  # Установить свой ключ
    
    # Кеш цен
    _cache: Dict[str, tuple[float, datetime]] = {}
    _cache_ttl = timedelta(hours=1)
    
    @staticmethod
    async def get_prices(market_hash_names: List[str]) -> Dict[str, float]:
        """
        Получить реальные цены из Steam Market
        
        Args:
            market_hash_names: Список названий предметов
            
        Returns:
            Dict с ценами в рублях
        """
        prices = {}
        uncached = []
        
        # Проверяем кеш
        for name in market_hash_names:
            cached = SteamAPIsPriceService._get_from_cache(name)
            if cached > 0:
                prices[name] = cached
            else:
                uncached.append(name)
        
        if not uncached:
            print(f"[STEAMAPIS] Все {len(prices)} цен из кеша")
            return prices
        
        print(f"[STEAMAPIS] Загружаем {len(uncached)} цен")
        
        # Получаем цены пачками (по 50 за раз)
        batch_size = 50
        for i in range(0, len(uncached), batch_size):
            batch = uncached[i:i + batch_size]
            batch_prices = await SteamAPIsPriceService._fetch_batch(batch)
            
            for name, price in batch_prices.items():
                if price > 0:
                    prices[name] = price
                    SteamAPIsPriceService._save_to_cache(name, price)
            
            # Небольшая задержка между пачками
            if i + batch_size < len(uncached):
                await asyncio.sleep(0.5)
        
        # Для предметов без цены возвращаем 0
        for name in market_hash_names:
            if name not in prices:
                prices[name] = 0.0
        
        successful = len([p for p in prices.values() if p > 0])
        print(f"[STEAMAPIS] Получено {successful}/{len(market_hash_names)} цен")
        
        return prices
    
    @staticmethod
    async def _fetch_batch(names: List[str]) -> Dict[str, float]:
        """Получить цены для пачки предметов через Steam Market API"""
        prices = {}
        
        # Используем прямой Steam Market API (бесплатный)
        base_url = "https://steamcommunity.com/market/priceoverview/"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                # Запрашиваем цены по одному предмету (Steam не поддерживает batch)
                for name in names:
                    try:
                        params = {
                            "appid": 730,
                            "currency": 5,  # RUB
                            "market_hash_name": name
                        }
                        
                        response = await client.get(base_url, params=params)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if data.get("success"):
                                # Берем median_price (средняя цена)
                                price_str = data.get("median_price", "0")
                                
                                # Парсим цену (формат: "1 234,56 pуб.")
                                price_str = price_str.replace(" ", "").replace("pуб.", "").replace("руб.", "").replace(",", ".")
                                
                                try:
                                    price_rub = float(price_str)
                                    if price_rub > 0:
                                        prices[name] = price_rub
                                        print(f"[STEAM_MARKET] {name}: {price_rub:.2f} ₽")
                                except ValueError:
                                    pass
                        
                        # Задержка чтобы не словить rate limit (Steam ограничивает ~20 req/min)
                        await asyncio.sleep(3.5)
                        
                    except Exception as e:
                        print(f"[STEAM_MARKET] Ошибка для {name}: {e}")
                        continue
                
                print(f"[STEAM_MARKET] Получено {len(prices)}/{len(names)} цен")
                    
        except Exception as e:
            print(f"[STEAM_MARKET] Общая ошибка: {e}")
        
        return prices
    
    @staticmethod
    async def get_single_price(market_hash_name: str) -> float:
        """
        Получить цену одного предмета
        Используется для точечных запросов
        """
        # Проверяем кеш
        cached = SteamAPIsPriceService._get_from_cache(market_hash_name)
        if cached > 0:
            return cached
        
        url = f"https://api.steamapis.com/market/item/730/{market_hash_name}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        
        if SteamAPIsPriceService.API_KEY:
            headers["X-API-KEY"] = SteamAPIsPriceService.API_KEY
        
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    price_usd = data.get("median_price", 0) or data.get("lowest_price", 0)
                    
                    if price_usd > 0:
                        price_rub = price_usd * 90
                        SteamAPIsPriceService._save_to_cache(market_hash_name, price_rub)
                        return price_rub
                        
        except Exception as e:
            print(f"[STEAMAPIS] Ошибка для {market_hash_name}: {e}")
        
        return 0.0
    
    @staticmethod
    def _get_from_cache(name: str) -> float:
        """Получить из кеша"""
        if name in SteamAPIsPriceService._cache:
            price, timestamp = SteamAPIsPriceService._cache[name]
            if datetime.now() - timestamp < SteamAPIsPriceService._cache_ttl:
                return price
        return 0.0
    
    @staticmethod
    def _save_to_cache(name: str, price: float):
        """Сохранить в кеш"""
        SteamAPIsPriceService._cache[name] = (price, datetime.now())
    
    @staticmethod
    def clear_cache():
        """Очистить кеш"""
        SteamAPIsPriceService._cache.clear()
        print("[STEAMAPIS] Кеш очищен")
    
    @staticmethod
    def set_api_key(api_key: str):
        """Установить API ключ"""
        SteamAPIsPriceService.API_KEY = api_key
        print(f"[STEAMAPIS] API ключ установлен")
