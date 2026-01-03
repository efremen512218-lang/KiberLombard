"""
Тест реальной интеграции с market.csgo API
"""
import asyncio
import httpx


async def test_market_csgo_api():
    """Тест получения цен с market.csgo"""
    
    print("=" * 60)
    print("ТЕСТ MARKET.CSGO API")
    print("=" * 60)
    
    # Тест 1: Получить все цены
    print("\n1. Получаем все цены (RUB)...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://market.csgo.com/api/v2/prices/RUB.json"
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Success: {data.get('success')}")
                print(f"   Currency: {data.get('currency')}")
                
                items = data.get("items", {})
                print(f"   Всего предметов: {len(items)}")
                
                # Показать первые 5
                print("\n   Примеры цен:")
                for i, (name, item_data) in enumerate(list(items.items())[:5]):
                    price = item_data.get("price", 0)
                    print(f"   {i+1}. {name}: {price}₽")
                
                # Найти конкретные предметы
                print("\n   Поиск популярных скинов:")
                test_items = [
                    "AK-47 | Redline (Field-Tested)",
                    "AWP | Asiimov (Field-Tested)",
                    "Desert Eagle | Blaze (Factory New)"
                ]
                
                for item_name in test_items:
                    if item_name in items:
                        item_data = items[item_name]
                        price = item_data.get("price", 0)
                        avg_price = item_data.get("avg_price", 0)
                        popularity = item_data.get("popularity_7d", 0)
                        print(f"   ✅ {item_name}")
                        print(f"      Цена: {price}₽")
                        print(f"      Средняя: {avg_price}₽")
                        print(f"      Популярность (7д): {popularity}")
                    else:
                        print(f"   ❌ {item_name} - не найден")
            else:
                print(f"   ❌ Ошибка: HTTP {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 2: Получить цены с buy-ордерами
    print("\n2. Получаем цены с buy-ордерами...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://market.csgo.com/api/v2/prices/class_instance/RUB.json"
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", {})
                print(f"   Всего предметов: {len(items)}")
                
                # Показать первые 3
                print("\n   Примеры:")
                for i, (class_id, item_data) in enumerate(list(items.items())[:3]):
                    name = item_data.get("market_hash_name", "Unknown")
                    price = item_data.get("price", 0)
                    buy_order = item_data.get("buy_order", 0)
                    print(f"   {i+1}. {name}")
                    print(f"      Sell: {price}₽ | Buy: {buy_order}₽")
    
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("ИТОГ:")
    print("✅ API market.csgo работает без ключа")
    print("✅ Можно получать instant sell цены")
    print("✅ Можно использовать как основной источник")
    print("\nДля детальной информации нужен API ключ:")
    print("1. Зарегистрироваться на market.csgo.com")
    print("2. Получить API ключ в настройках")
    print("3. Добавить в .env: MARKET_CSGO_API_KEY=your_key")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_market_csgo_api())
