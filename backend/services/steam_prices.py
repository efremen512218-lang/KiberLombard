"""
Получение справочных цен с Steam Market
ОТКЛЮЧЕНО: Слишком медленно (1 запрос = 3.5 сек)
Используем market.csgo вместо этого
"""
from typing import Dict, List


class SteamPriceService:
    """Сервис для получения справочных цен с Steam Market (ОТКЛЮЧЕН)"""
    
    @staticmethod
    async def get_prices(market_hash_names: List[str]) -> Dict[str, float]:
        """
        ОТКЛЮЧЕНО - возвращаем пустой словарь
        Используем market.csgo как единственный источник цен
        """
        # Возвращаем 0 для всех предметов
        # Реальные цены берутся из market.csgo
        return {name: 0.0 for name in market_hash_names}
    
    @staticmethod
    def clear_cache():
        """Ничего не делаем"""
        pass
