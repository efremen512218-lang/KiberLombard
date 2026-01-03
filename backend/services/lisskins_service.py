"""
Интеграция с Lis-Skins для получения instant sell цен
УПРОЩЕНО: Используем цены market.csgo + наценка 10% как оценку Lis-Skins
"""
import httpx
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class LisSkinsService:
    """Сервис для получения instant sell цен с Lis-Skins"""
    
    # Lis-Skins обычно на 5-15% дороже market.csgo
    # Используем 10% как среднее
    MARKUP_OVER_MARKET_CSGO = 1.10
    
    @staticmethod
    async def get_prices(market_hash_names: List[str]) -> Dict[str, float]:
        """
        Получить instant sell цены с Lis-Skins
        
        Пока нет API ключа - используем цены market.csgo + 10% наценка
        Это консервативная оценка (реальные цены Lis-Skins обычно выше)
        
        Args:
            market_hash_names: Список названий предметов
            
        Returns:
            Dict с ценами в рублях (instant sell)
        """
        from services.market_csgo_service import MarketCSGOService
        
        # Получаем цены с market.csgo
        market_prices = await MarketCSGOService.get_prices(market_hash_names)
        
        # Добавляем наценку 10% (Lis-Skins обычно дороже)
        prices = {}
        for name, price in market_prices.items():
            if price > 0:
                prices[name] = price * LisSkinsService.MARKUP_OVER_MARKET_CSGO
            else:
                prices[name] = 0.0
        
        successful = len([p for p in prices.values() if p > 0])
        print(f"[LIS-SKINS] Оценка для {successful}/{len(market_hash_names)} предметов")
        
        return prices
    
    @staticmethod
    def clear_cache():
        """Очистить кэш (делегируем в market.csgo)"""
        from services.market_csgo_service import MarketCSGOService
        MarketCSGOService.clear_cache()
