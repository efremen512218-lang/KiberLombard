"""
Сервис расчёта условий сделки с конфигурируемыми параметрами
"""
from typing import List, Dict
from datetime import datetime, timedelta
from config import get_settings


class PricingService:
    """Расчёт условий выдачи и выкупа"""
    
    @staticmethod
    def get_purchase_coefficient(instant_price: float) -> float:
        """
        Получить коэффициент покупки
        
        Модель: 40% от instant sell цены
        Это обеспечивает:
        - Высокую маржу при дефолте (~164%)
        - Гарантированную прибыль
        - Соответствие рынку ломбардов (30-50%)
        
        Args:
            instant_price: Instant sell цена на Lis-Skins/market.csgo
            
        Returns:
            Коэффициент покупки (всегда 0.40)
        """
        return 0.40  # 40% от instant sell цены
    
    @staticmethod
    def get_loan_percent(instant_price: float) -> float:
        """
        Алиас для get_purchase_coefficient (для обратной совместимости)
        
        Args:
            instant_price: Instant цена предмета
            
        Returns:
            Процент выдачи (всегда 0.40)
        """
        return 0.40  # 40%
    
    @staticmethod
    def get_term_config(days: int) -> Dict:
        """
        Получить конфигурацию для срока
        
        Если точного значения нет, делает линейную интерполяцию
        
        Args:
            days: Количество дней (7-30)
            
        Returns:
            {"interest": float, "premium": float}
        """
        settings = get_settings()
        terms = settings.get_buyback_terms()
        
        # Если есть точное значение
        if days in terms:
            return terms[days]
        
        # Линейная интерполяция между ближайшими значениями
        sorted_days = sorted(terms.keys())
        
        # Найти ближайшие значения
        lower = None
        upper = None
        
        for d in sorted_days:
            if d < days:
                lower = d
            elif d > days:
                upper = d
                break
        
        if lower is None:
            return terms[sorted_days[0]]
        if upper is None:
            return terms[sorted_days[-1]]
        
        # Интерполяция
        lower_config = terms[lower]
        upper_config = terms[upper]
        
        ratio = (days - lower) / (upper - lower)
        
        return {
            "interest": lower_config["interest"] + ratio * (upper_config["interest"] - lower_config["interest"]),
            "premium": lower_config["premium"] + ratio * (upper_config["premium"] - lower_config["premium"])
        }
    
    @staticmethod
    def calculate_quote(items: List[Dict], option_days: int) -> Dict:
        """
        Рассчитать условия сделки
        
        Args:
            items: Список предметов с ценами
            option_days: Срок опциона (7-30 дней)
            
        Returns:
            Dict с условиями сделки
        """
        # Рассчитываем для каждого предмета
        market_total = 0.0
        loan_total = 0.0
        
        items_with_loan = []
        
        for item in items:
            instant_price = item.get("instant_price", 0.0)
            
            if instant_price > 0:
                # Процент выдачи зависит от цены
                loan_percent = PricingService.get_loan_percent(instant_price)
                loan_price = instant_price * loan_percent
                
                items_with_loan.append({
                    **item,
                    "loan_percent": loan_percent,
                    "loan_price": loan_price
                })
                
                market_total += instant_price
                loan_total += loan_price
        
        # Рассчитываем выкуп
        term_config = PricingService.get_term_config(option_days)
        
        base_buyback = loan_total * (1 + term_config["interest"])
        buyback_price = base_buyback * (1 + term_config["premium"])
        
        # Дата окончания
        option_expiry = datetime.now() + timedelta(days=option_days)
        
        return {
            "market_total": round(market_total, 2),
            "loan_amount": round(loan_total, 2),
            "buyback_price": round(buyback_price, 2),
            "option_days": option_days,
            "option_expiry": option_expiry,
            "term_config": term_config,
            "items": items_with_loan
        }
    
    @staticmethod
    def check_kyc_required(loan_amount: float) -> bool:
        """
        Проверить требуется ли паспорт
        
        В новой модели паспорт требуется ВСЕГДА
        """
        return True  # Всегда требуем паспорт

    @staticmethod
    def calculate_profit_default(instant_sell_price: float, purchase_price: float) -> dict:
        """
        Рассчитать прибыль при дефолте (продажа на Lis-Skins)
        
        Args:
            instant_sell_price: Цена instant sell на Lis-Skins
            purchase_price: Сумма, выданная пользователю
            
        Returns:
            Dict с расчётом прибыли
        """
        LIS_SKINS_COMMISSION = 0.04  # 4%
        
        commission = instant_sell_price * LIS_SKINS_COMMISSION
        net_revenue = instant_sell_price - commission
        profit = net_revenue - purchase_price
        margin = (profit / purchase_price) * 100 if purchase_price > 0 else 0
        
        return {
            "instant_sell_price": round(instant_sell_price, 2),
            "purchase_price": round(purchase_price, 2),
            "commission": round(commission, 2),
            "net_revenue": round(net_revenue, 2),
            "profit": round(profit, 2),
            "margin_percent": round(margin, 2)
        }
    
    @staticmethod
    def calculate_profit_buyback(purchase_price: float, term_days: int) -> dict:
        """
        Рассчитать прибыль при выкупе
        
        Args:
            purchase_price: Сумма, выданная пользователю
            term_days: Срок сделки в днях
            
        Returns:
            Dict с расчётом прибыли
        """
        term_config = PricingService.get_term_config(term_days)
        
        base_buyback = purchase_price * (1 + term_config["interest"])
        buyback_price = base_buyback * (1 + term_config["premium"])
        
        profit = buyback_price - purchase_price
        margin = (profit / purchase_price) * 100 if purchase_price > 0 else 0
        annual_rate = margin * (365 / term_days) if term_days > 0 else 0
        
        return {
            "purchase_price": round(purchase_price, 2),
            "interest_percent": round(term_config["interest"] * 100, 2),
            "premium_percent": round(term_config["premium"] * 100, 2),
            "buyback_price": round(buyback_price, 2),
            "profit": round(profit, 2),
            "margin_percent": round(margin, 2),
            "annual_rate_percent": round(annual_rate, 2)
        }
    
    @staticmethod
    def calculate_deal_profitability(items: List[dict], term_days: int, default_rate: float = 0.5) -> dict:
        """
        Рассчитать ожидаемую прибыльность сделки
        
        Args:
            items: Список предметов с instant_price
            term_days: Срок сделки
            default_rate: Процент дефолтов (0.5 = 50%)
            
        Returns:
            Dict с анализом прибыльности
        """
        total_instant = sum(item.get("instant_price", 0) for item in items)
        total_purchase = sum(
            item.get("instant_price", 0) * PricingService.get_purchase_coefficient(item.get("instant_price", 0))
            for item in items
        )
        
        # Прибыль при дефолте
        default_profit = PricingService.calculate_profit_default(total_instant, total_purchase)
        
        # Прибыль при выкупе
        buyback_profit = PricingService.calculate_profit_buyback(total_purchase, term_days)
        
        # Ожидаемая прибыль (взвешенная)
        expected_profit = (
            default_profit["profit"] * default_rate +
            buyback_profit["profit"] * (1 - default_rate)
        )
        expected_margin = (expected_profit / total_purchase) * 100 if total_purchase > 0 else 0
        
        return {
            "total_instant_sell": round(total_instant, 2),
            "total_purchase": round(total_purchase, 2),
            "default_scenario": default_profit,
            "buyback_scenario": buyback_profit,
            "expected_profit": round(expected_profit, 2),
            "expected_margin_percent": round(expected_margin, 2),
            "default_rate_assumed": default_rate
        }
