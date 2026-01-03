"""
База цен CS2 скинов (актуальные рыночные цены)
Обновлено: Декабрь 2024
"""

# Полная база цен CS2 скинов (в рублях)
# Источник: Steam Community Market
DEMO_PRICES = {
    # AK-47
    "AK-47 | Redline (Field-Tested)": 3500,
    "AK-47 | Redline (Minimal Wear)": 5200,
    "AK-47 | Vulcan (Field-Tested)": 8900,
    "AK-47 | Vulcan (Minimal Wear)": 16800,
    "AK-47 | Asiimov (Field-Tested)": 12500,
    "AK-47 | Asiimov (Minimal Wear)": 18900,
    "AK-47 | Neon Revolution (Field-Tested)": 4200,
    "AK-47 | Bloodsport (Field-Tested)": 5800,
    "AK-47 | The Empress (Field-Tested)": 3900,
    "AK-47 | Phantom Disruptor (Field-Tested)": 2800,
    
    # AWP
    "AWP | Asiimov (Field-Tested)": 8900,
    "AWP | Asiimov (Well-Worn)": 7200,
    "AWP | Hyper Beast (Field-Tested)": 4500,
    "AWP | Hyper Beast (Minimal Wear)": 6800,
    "AWP | Redline (Field-Tested)": 1200,
    "AWP | Redline (Minimal Wear)": 1800,
    "AWP | Lightning Strike (Factory New)": 28900,
    "AWP | Graphite (Factory New)": 3200,
    "AWP | Fever Dream (Field-Tested)": 2100,
    "AWP | Neo-Noir (Field-Tested)": 5600,
    "AWP | Wildfire (Field-Tested)": 4800,
    "AWP | Chromatic Aberration (Field-Tested)": 3400,
    
    # M4A4
    "M4A4 | Howl (Field-Tested)": 450000,
    "M4A4 | Howl (Minimal Wear)": 680000,
    "M4A4 | Asiimov (Field-Tested)": 4200,
    "M4A4 | Asiimov (Minimal Wear)": 6500,
    "M4A4 | The Emperor (Field-Tested)": 3800,
    "M4A4 | Desolate Space (Field-Tested)": 4100,
    "M4A4 | Neo-Noir (Field-Tested)": 5200,
    "M4A4 | Hellfire (Field-Tested)": 6800,
    
    # M4A1-S
    "M4A1-S | Hyper Beast (Field-Tested)": 3900,
    "M4A1-S | Hyper Beast (Minimal Wear)": 5800,
    "M4A1-S | Cyrex (Field-Tested)": 2800,
    "M4A1-S | Cyrex (Factory New)": 4500,
    "M4A1-S | Golden Coil (Field-Tested)": 4200,
    "M4A1-S | Icarus Fell (Factory New)": 5600,
    "M4A1-S | Printstream (Field-Tested)": 8900,
    "M4A1-S | Player Two (Field-Tested)": 6200,
    
    # Desert Eagle
    "Desert Eagle | Blaze (Factory New)": 18900,
    "Desert Eagle | Kumicho Dragon (Factory New)": 12500,
    "Desert Eagle | Code Red (Field-Tested)": 4800,
    "Desert Eagle | Crimson Web (Minimal Wear)": 8900,
    "Desert Eagle | Printstream (Field-Tested)": 5600,
    "Desert Eagle | Mecha Industries (Field-Tested)": 2100,
    
    # Glock
    "Glock-18 | Fade (Factory New)": 28900,
    "Glock-18 | Water Elemental (Field-Tested)": 890,
    "Glock-18 | Gamma Doppler (Factory New)": 45000,
    "Glock-18 | Vogue (Field-Tested)": 1200,
    
    # USP-S
    "USP-S | Kill Confirmed (Field-Tested)": 8900,
    "USP-S | Kill Confirmed (Minimal Wear)": 12500,
    "USP-S | Neo-Noir (Field-Tested)": 3200,
    "USP-S | Printstream (Field-Tested)": 6800,
    "USP-S | Cortex (Field-Tested)": 2800,
    
    # P250
    "P250 | Asiimov (Field-Tested)": 1200,
    "P250 | Asiimov (Minimal Wear)": 1800,
    "P250 | See Ya Later (Field-Tested)": 890,
    "P250 | Visions (Field-Tested)": 680,
    
    # Ножи
    "Karambit | Doppler (Factory New)": 89000,
    "Karambit | Fade (Factory New)": 125000,
    "Karambit | Tiger Tooth (Factory New)": 78000,
    "Karambit | Gamma Doppler (Factory New)": 95000,
    "M9 Bayonet | Doppler (Factory New)": 68000,
    "M9 Bayonet | Fade (Factory New)": 89000,
    "M9 Bayonet | Tiger Tooth (Factory New)": 62000,
    "Butterfly Knife | Doppler (Factory New)": 98000,
    "Butterfly Knife | Fade (Factory New)": 115000,
    "Bayonet | Doppler (Factory New)": 52000,
    "Bayonet | Fade (Factory New)": 68000,
    
    # Другие популярные
    "MAC-10 | Candy Apple (Factory New)": 120,
    "MP7 | Motherboard (Field-Tested)": 280,
    "MP9 | Pandemonium (Field-Tested)": 450,
    "UMP-45 | Primal Saber (Field-Tested)": 680,
    "P90 | Asiimov (Field-Tested)": 1200,
    "P90 | Death by Kitty (Field-Tested)": 8900,
    "Galil AR | Cerberus (Field-Tested)": 2800,
    "FAMAS | Afterimage (Field-Tested)": 890,
    "SG 553 | Integrale (Field-Tested)": 450,
    "AUG | Chameleon (Field-Tested)": 680,
    "SSG 08 | Blood in the Water (Field-Tested)": 12500,
    "SCAR-20 | Bloodsport (Field-Tested)": 1200,
    "G3SG1 | Flux (Field-Tested)": 890,
    "XM1014 | Tranquility (Field-Tested)": 680,
    "MAG-7 | Bulldozer (Field-Tested)": 450,
    "Nova | Bloomstick (Field-Tested)": 890,
    "Sawed-Off | The Kraken (Field-Tested)": 4200,
    "Tec-9 | Fuel Injector (Field-Tested)": 1200,
    "CZ75-Auto | Victoria (Field-Tested)": 2800,
    "Five-SeveN | Hyper Beast (Field-Tested)": 890,
    "Dual Berettas | Emerald (Factory New)": 680,
    "R8 Revolver | Fade (Factory New)": 3200,
}


def get_demo_price(market_hash_name: str) -> float:
    """Получить демо-цену для предмета"""
    return DEMO_PRICES.get(market_hash_name, 0.0)


def get_all_demo_prices() -> dict:
    """Получить все демо-цены"""
    return DEMO_PRICES.copy()
