"""
Тест получения live цен
"""
import asyncio
from services.price_aggregator import PriceAggregator


async def test_prices():
    """Тест получения цен"""
    
    # Тестовые предметы
    items = [
        "AK-47 | Redline (Field-Tested)",
        "AWP | Asiimov (Field-Tested)",
        "M4A1-S | Hyper Beast (Field-Tested)",
        "Glock-18 | Fade (Factory New)",
        "Desert Eagle | Blaze (Factory New)"
    ]
    
    print("=" * 60)
    print("ТЕСТ ПОЛУЧЕНИЯ LIVE ЦЕН")
    print("=" * 60)
    
    prices = await PriceAggregator.get_prices(items)
    
    print("\nРезультаты:\n")
    
    for name, price_data in prices.items():
        print(f"\n{name}")
        print(f"  Steam Market:  {price_data.steam_price:>10.2f} ₽")
        print(f"  Lis-Skins:     {price_data.lis_price:>10.2f} ₽")
        print(f"  market.csgo:   {price_data.market_csgo_price:>10.2f} ₽")
        print(f"  ─────────────────────────────")
        print(f"  Instant цена:  {price_data.instant_price:>10.2f} ₽")
        print(f"  Источник:      {price_data.instant_source}")
        print(f"  Принимаем:     {'✅ ДА' if price_data.is_acceptable else '❌ НЕТ'}")
    
    print("\n" + "=" * 60)
    
    # Статистика
    acceptable = [p for p in prices.values() if p.is_acceptable]
    print(f"\nПринимаем: {len(acceptable)}/{len(prices)} предметов")
    
    if acceptable:
        total_instant = sum(p.instant_price for p in acceptable)
        print(f"Общая instant стоимость: {total_instant:.2f} ₽")


if __name__ == "__main__":
    asyncio.run(test_prices())
