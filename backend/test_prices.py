"""
Тест загрузки LIVE цен
"""
import asyncio
from services.live_prices import LivePriceService


async def test_prices():
    """Тест получения цен"""
    
    # Тестовые предметы
    test_items = [
        "AK-47 | Redline (Field-Tested)",
        "AWP | Asiimov (Field-Tested)",
        "M4A4 | Howl (Field-Tested)",
        "Desert Eagle | Blaze (Factory New)",
        "Glock-18 | Fade (Factory New)",
        "Karambit | Doppler (Factory New)",
        "M4A1-S | Hyper Beast (Field-Tested)",
        "P250 | Asiimov (Field-Tested)",
        "USP-S | Kill Confirmed (Minimal Wear)",
        "AK-47 | Vulcan (Minimal Wear)",
    ]
    
    print("=" * 80)
    print("ТЕСТ ЗАГРУЗКИ LIVE ЦЕН")
    print("=" * 80)
    print()
    
    # Получаем цены
    prices = await LivePriceService.get_prices(test_items)
    
    print()
    print("=" * 80)
    print("РЕЗУЛЬТАТЫ:")
    print("=" * 80)
    print()
    
    total = 0
    for item in test_items:
        price = prices.get(item, 0)
        status = "✅" if price > 0 else "❌"
        print(f"{status} {item}")
        if price > 0:
            print(f"   Цена: {price:,.2f} ₽")
            total += price
        else:
            print(f"   Цена не найдена")
        print()
    
    print("=" * 80)
    print(f"Успешно загружено: {len([p for p in prices.values() if p > 0])} из {len(test_items)}")
    print(f"Общая стоимость: {total:,.2f} ₽")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_prices())
