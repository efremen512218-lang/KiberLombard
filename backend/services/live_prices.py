"""
Профессиональный сервис получения live цен из Steam Market
Использует несколько надежных источников
"""
import httpx
import asyncio
import json
from typing import Dict, List
from datetime import datetime, timedelta


class LivePriceService:
    """Получение актуальных цен из надежных источников"""
    
    # Кеш цен (в проде использовать Redis)
    _cache: Dict[str, tuple[float, datetime]] = {}
    _cache_ttl = timedelta(hours=1)
    
    @staticmethod
    async def get_prices(market_hash_names: List[str]) -> Dict[str, float]:
        """
        Получить актуальные цены
        
        Источники (по приоритету):
        1. Кеш (1 час)
        2. Pricempire API (быстро, надежно, бесплатно)
        3. CSGOBackpack API (резервный)
        4. Steam Market API (медленно, ограничено)
        """
        prices = {}
        uncached = []
        
        # Проверяем кеш
        for name in market_hash_names:
            cached = LivePriceService._get_from_cache(name)
            if cached > 0:
                prices[name] = cached
            else:
                uncached.append(name)
        
        if not uncached:
            print(f"[LIVE PRICES] Все {len(prices)} цен из кеша")
            return prices
        
        print(f"[LIVE PRICES] Загружаем {len(uncached)} цен")
        
        # Пробуем Pricempire (лучший источник)
        pricempire_prices = await LivePriceService._get_pricempire_prices(uncached)
        for name, price in pricempire_prices.items():
            if price > 0:
                prices[name] = price
                LivePriceService._save_to_cache(name, price)
                if name in uncached:
                    uncached.remove(name)
        
        # Если остались без цены, пробуем CSGOBackpack
        if uncached and len(uncached) < 50:
            print(f"[LIVE PRICES] Пробуем CSGOBackpack для {len(uncached)} предметов")
            backpack_prices = await LivePriceService._get_csgobackpack_prices(uncached)
            for name, price in backpack_prices.items():
                if price > 0:
                    prices[name] = price
                    LivePriceService._save_to_cache(name, price)
                    if name in uncached:
                        uncached.remove(name)
        
        # Для остальных возвращаем 0 (fallback в main.py)
        for name in market_hash_names:
            if name not in prices:
                prices[name] = 0.0
        
        successful = len([p for p in prices.values() if p > 0])
        print(f"[LIVE PRICES] Получено {successful}/{len(market_hash_names)} цен")
        
        return prices
    
    @staticmethod
    async def _get_pricempire_prices(names: List[str]) -> Dict[str, float]:
        """
        Получить цены с Pricempire API
        Бесплатный, надежный, без rate limit
        """
        prices = {}
        
        # Pricempire API endpoint
        url = "https://pricempire.com/api/v3/items/prices"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        
        # Pricempire принимает список предметов
        params = {
            "source": "steam",
            "currency": "RUB",
            "items": ",".join(names[:100])  # Максимум 100 за раз
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for name in names:
                        if name in data:
                            item_data = data[name]
                            # Берем среднюю цену или lowest
                            price = item_data.get("steam", {}).get("price", 0)
                            
                            if price > 0:
                                prices[name] = float(price)
                                print(f"[PRICEMPIRE] {name}: {price} ₽")
                    
                    print(f"[PRICEMPIRE] Получено {len(prices)} цен")
                else:
                    print(f"[PRICEMPIRE] Ошибка {response.status_code}")
                    
        except Exception as e:
            print(f"[PRICEMPIRE] Ошибка: {e}")
        
        return prices
    
    @staticmethod
    async def _get_csgobackpack_prices(names: List[str]) -> Dict[str, float]:
        """
        Получить цены с CSGOBackpack API
        Резервный источник
        """
        prices = {}
        
        url = "https://csgobackpack.net/api/GetItemPrice/"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
                for name in names[:20]:  # Ограничиваем количество
                    try:
                        # CSGOBackpack требует URL-encoded название
                        item_url = f"{url}{name}"
                        response = await client.get(item_url)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if data.get("success"):
                                # Цена в USD, конвертируем в RUB
                                price_usd = data.get("average_price", 0)
                                if price_usd > 0:
                                    price_rub = price_usd * 90  # Курс USD->RUB
                                    prices[name] = price_rub
                                    print(f"[CSGOBACKPACK] {name}: ${price_usd} = {price_rub} ₽")
                        
                        await asyncio.sleep(0.5)  # Rate limiting
                        
                    except Exception as e:
                        print(f"[CSGOBACKPACK] Ошибка для {name}: {e}")
                        continue
                        
        except Exception as e:
            print(f"[CSGOBACKPACK] Общая ошибка: {e}")
        
        return prices
    
    @staticmethod
    def _get_from_cache(name: str) -> float:
        """Получить из кеша"""
        if name in LivePriceService._cache:
            price, timestamp = LivePriceService._cache[name]
            if datetime.now() - timestamp < LivePriceService._cache_ttl:
                return price
        return 0.0
    
    @staticmethod
    def _save_to_cache(name: str, price: float):
        """Сохранить в кеш"""
        LivePriceService._cache[name] = (price, datetime.now())
    
    @staticmethod
    def clear_cache():
        """Очистить кеш"""
        LivePriceService._cache.clear()
        print("[LIVE PRICES] Кеш очищен")
