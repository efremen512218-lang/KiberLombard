"""
Умная оценка цен на основе паттернов и редкости
"""
import re
from typing import Optional


class SmartPriceEstimator:
    """Оценка цен на основе названия, редкости и состояния"""
    
    # Базовые цены по типу оружия (в рублях)
    WEAPON_BASE_PRICES = {
        # Винтовки
        "AK-47": 500,
        "M4A4": 400,
        "M4A1-S": 400,
        "AWP": 600,
        "SSG 08": 150,
        "SCAR-20": 200,
        "G3SG1": 180,
        "Galil AR": 120,
        "FAMAS": 120,
        "AUG": 150,
        "SG 553": 150,
        
        # Пистолеты
        "Desert Eagle": 250,
        "USP-S": 200,
        "P2000": 80,
        "Glock-18": 150,
        "P250": 100,
        "Five-SeveN": 120,
        "Tec-9": 100,
        "CZ75-Auto": 150,
        "Dual Berettas": 80,
        "R8 Revolver": 120,
        
        # ПП
        "MP9": 80,
        "MAC-10": 70,
        "MP7": 100,
        "MP5-SD": 120,
        "UMP-45": 90,
        "P90": 150,
        "PP-Bizon": 80,
        
        # Дробовики
        "Nova": 70,
        "XM1014": 100,
        "Sawed-Off": 80,
        "MAG-7": 90,
        
        # Пулеметы
        "M249": 120,
        "Negev": 100,
        
        # Ножи (базовая цена)
        "Karambit": 50000,
        "M9 Bayonet": 40000,
        "Bayonet": 35000,
        "Butterfly Knife": 45000,
        "Flip Knife": 30000,
        "Gut Knife": 25000,
        "Falchion Knife": 28000,
        "Bowie Knife": 30000,
        "Huntsman Knife": 32000,
        "Shadow Daggers": 28000,
        "Navaja Knife": 25000,
        "Stiletto Knife": 35000,
        "Talon Knife": 40000,
        "Ursus Knife": 32000,
        "Nomad Knife": 35000,
        "Paracord Knife": 33000,
        "Survival Knife": 34000,
        "Skeleton Knife": 38000,
        "Classic Knife": 42000,
        
        # Перчатки
        "Gloves": 30000,
    }
    
    # Множители по редкости
    RARITY_MULTIPLIERS = {
        "Contraband": 100.0,      # Контрабанда (M4A4 Howl)
        "Covert": 8.0,            # Тайное (красные)
        "Classified": 3.0,        # Засекреченное (розовые)
        "Restricted": 1.5,        # Запрещённое (фиолетовые)
        "Mil-Spec Grade": 0.8,    # Армейское (синие)
        "Mil-Spec": 0.8,
        "Industrial Grade": 0.3,  # Промышленное (голубые)
        "Consumer Grade": 0.15,   # Ширпотреб (белые)
    }
    
    # Множители по состоянию (wear)
    WEAR_MULTIPLIERS = {
        "Factory New": 1.5,
        "Minimal Wear": 1.2,
        "Field-Tested": 1.0,
        "Well-Worn": 0.7,
        "Battle-Scarred": 0.5,
    }
    
    # Популярные коллекции (бонус к цене)
    POPULAR_COLLECTIONS = {
        "Asiimov": 1.5,
        "Redline": 1.3,
        "Hyper Beast": 1.4,
        "Fade": 2.0,
        "Doppler": 1.8,
        "Tiger Tooth": 1.6,
        "Marble Fade": 2.2,
        "Crimson Web": 1.7,
        "Case Hardened": 1.5,
        "Fire Serpent": 3.0,
        "Howl": 100.0,
        "Dragon Lore": 80.0,
        "Medusa": 50.0,
        "Gungnir": 60.0,
        "The Prince": 40.0,
        "Wild Lotus": 35.0,
        "Printstream": 1.6,
        "Neo-Noir": 1.4,
        "Vulcan": 1.5,
        "Kill Confirmed": 1.6,
        "Blaze": 1.8,
        "Gamma Doppler": 2.0,
        "Autotronic": 1.5,
        "Bloodsport": 1.4,
    }
    
    @staticmethod
    def estimate_price(market_hash_name: str, rarity: Optional[str] = None) -> float:
        """
        Оценить цену предмета на основе названия и редкости
        
        Args:
            market_hash_name: Полное название предмета
            rarity: Редкость предмета
            
        Returns:
            Оценочная цена в рублях
        """
        # Проверяем специальные случаи
        if "★" in market_hash_name or "Knife" in market_hash_name:
            return SmartPriceEstimator._estimate_knife_price(market_hash_name)
        
        if "Gloves" in market_hash_name or "Wraps" in market_hash_name:
            return SmartPriceEstimator._estimate_gloves_price(market_hash_name)
        
        # Обычное оружие
        return SmartPriceEstimator._estimate_weapon_price(market_hash_name, rarity)
    
    @staticmethod
    def _estimate_weapon_price(name: str, rarity: Optional[str]) -> float:
        """Оценка цены обычного оружия"""
        # Извлекаем оружие и скин
        parts = name.split("|")
        if len(parts) < 2:
            return 100.0  # Минимальная цена
        
        weapon = parts[0].strip()
        skin_and_wear = parts[1].strip()
        
        # Базовая цена оружия
        base_price = SmartPriceEstimator.WEAPON_BASE_PRICES.get(weapon, 150.0)
        
        # Множитель редкости
        rarity_mult = 1.0
        if rarity:
            rarity_mult = SmartPriceEstimator.RARITY_MULTIPLIERS.get(rarity, 1.0)
        
        # Множитель состояния
        wear_mult = 1.0
        for wear, mult in SmartPriceEstimator.WEAR_MULTIPLIERS.items():
            if wear in name:
                wear_mult = mult
                break
        
        # Бонус за популярную коллекцию
        collection_mult = 1.0
        for collection, mult in SmartPriceEstimator.POPULAR_COLLECTIONS.items():
            if collection in name:
                collection_mult = mult
                break
        
        # Итоговая цена
        price = base_price * rarity_mult * wear_mult * collection_mult
        
        # Минимум 50 рублей
        return max(50.0, round(price, 2))
    
    @staticmethod
    def _estimate_knife_price(name: str) -> float:
        """Оценка цены ножа"""
        # Базовая цена ножа
        base_price = 30000.0
        
        # Определяем тип ножа
        for knife_type, price in SmartPriceEstimator.WEAPON_BASE_PRICES.items():
            if knife_type in name and "Knife" in knife_type:
                base_price = price
                break
        
        # Множитель за скин
        skin_mult = 1.0
        for collection, mult in SmartPriceEstimator.POPULAR_COLLECTIONS.items():
            if collection in name:
                skin_mult = mult
                break
        
        # Множитель состояния
        wear_mult = 1.0
        for wear, mult in SmartPriceEstimator.WEAR_MULTIPLIERS.items():
            if wear in name:
                wear_mult = mult
                break
        
        # Vanilla ножи (без скина) дешевле
        if "Vanilla" in name or "|" not in name:
            skin_mult = 0.7
        
        price = base_price * skin_mult * wear_mult
        
        # Минимум 20,000 для ножей
        return max(20000.0, round(price, 2))
    
    @staticmethod
    def _estimate_gloves_price(name: str) -> float:
        """Оценка цены перчаток"""
        base_price = 30000.0
        
        # Множитель за скин
        skin_mult = 1.0
        for collection, mult in SmartPriceEstimator.POPULAR_COLLECTIONS.items():
            if collection in name:
                skin_mult = mult
                break
        
        # Множитель состояния
        wear_mult = 1.0
        for wear, mult in SmartPriceEstimator.WEAR_MULTIPLIERS.items():
            if wear in name:
                wear_mult = mult
                break
        
        price = base_price * skin_mult * wear_mult
        
        # Минимум 15,000 для перчаток
        return max(15000.0, round(price, 2))


def get_smart_price(market_hash_name: str, rarity: Optional[str] = None) -> float:
    """Получить умную оценку цены"""
    return SmartPriceEstimator.estimate_price(market_hash_name, rarity)
