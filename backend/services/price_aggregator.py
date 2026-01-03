"""
Агрегатор цен - ОПТИМИЗИРОВАННАЯ ВЕРСИЯ
Используем market.csgo как единственный источник цен
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class PriceData:
    """Данные о цене предмета"""
    market_csgo_price: float  # Цена на market.csgo (основа для залога)
    lis_skins_estimate: float  # Оценка цены на Lis-Skins (+10%)
    instant_price: float  # = market_csgo_price (для залога)
    is_acceptable: bool  # Можно ли принять предмет
    timestamp: datetime


class PriceAggregator:
    """Получение цен из market.csgo"""
    
    MIN_PRICE = 40.0  # Минимальная цена для приёма (залог будет 20₽)
    LIS_SKINS_MARKUP = 1.10  # Lis-Skins обычно на 10% дороже
    
    @staticmethod
    async def get_prices(market_hash_names: List[str]) -> Dict[str, PriceData]:
        """
        Получить цены для списка предметов
        
        Логика:
        1. Берём цену с market.csgo (бесплатный API)
        2. Оцениваем цену Lis-Skins как market.csgo + 10%
        3. Залог = market.csgo × 50%
        
        Returns:
            Dict[market_hash_name, PriceData]
        """
        from services.market_csgo_service import MarketCSGOService
        
        print(f"[PRICES] Получаем цены для {len(market_hash_names)} предметов")
        
        # Получаем цены с market.csgo (кэшируется на 1 час)
        market_prices = await MarketCSGOService.get_prices(market_hash_names)
        
        # Формируем результат
        result = {}
        acceptable_count = 0
        
        for name in market_hash_names:
            market_price = market_prices.get(name, 0.0)
            lis_estimate = market_price * PriceAggregator.LIS_SKINS_MARKUP if market_price > 0 else 0.0
            
            # Принимаем если цена >= 40₽ (залог будет >= 20₽)
            is_acceptable = market_price >= PriceAggregator.MIN_PRICE
            
            if is_acceptable:
                acceptable_count += 1
            
            result[name] = PriceData(
                market_csgo_price=market_price,
                lis_skins_estimate=lis_estimate,
                instant_price=market_price,  # Для залога используем market.csgo
                is_acceptable=is_acceptable,
                timestamp=datetime.now()
            )
        
        print(f"[PRICES] ✅ Принимаем {acceptable_count}/{len(market_hash_names)} предметов (цена >= {PriceAggregator.MIN_PRICE}₽)")
        
        return result
    
    @staticmethod
    def calculate_loan(price: float) -> float:
        """Рассчитать сумму залога (40% от цены)"""
        return price * 0.40
    
    @staticmethod
    def calculate_profit_on_default(market_csgo_price: float) -> dict:
        """
        Рассчитать прибыль при дефолте (продажа на Lis-Skins)
        
        Args:
            market_csgo_price: Цена на market.csgo
            
        Returns:
            Dict с расчётом прибыли
        """
        loan = market_csgo_price * 0.50  # Выдали 50%
        lis_price = market_csgo_price * 1.10  # Lis-Skins +10%
        lis_commission = lis_price * 0.04  # Комиссия 4%
        net_revenue = lis_price - lis_commission
        profit = net_revenue - loan
        margin = (profit / loan) * 100 if loan > 0 else 0
        
        return {
            "loan_given": round(loan, 2),
            "lis_skins_price": round(lis_price, 2),
            "lis_commission": round(lis_commission, 2),
            "net_revenue": round(net_revenue, 2),
            "profit": round(profit, 2),
            "margin_percent": round(margin, 2)
        }
