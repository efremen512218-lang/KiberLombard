"""
Тестовый скрипт для проверки загрузки инвентаря
"""
import asyncio
from services.steam_authenticated_inventory import SteamAuthenticatedInventory
from services.steam_service import SteamService


async def test_public_inventory():
    """Тест публичного метода"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Публичный метод загрузки")
    print("="*60)
    
    # Тестовый Steam ID (замени на свой)
    steam_id = "76561198306528518"
    
    print(f"\n📥 Загружаем инвентарь для Steam ID: {steam_id}")
    
    items = await SteamAuthenticatedInventory.get_inventory_public(
        steam_id=steam_id,
        retry_count=3
    )
    
    if items:
        print(f"\n✅ Успешно загружено {len(items)} предметов!")
        print("\nПервые 3 предмета:")
        for i, item in enumerate(items[:3], 1):
            print(f"{i}. {item['name']} - {item['market_hash_name']}")
    else:
        print("\n⚠️ Инвентарь пустой или недоступен")
    
    return items


async def test_main_service():
    """Тест основного сервиса (с автоматическим выбором метода)"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Основной сервис (автоматический выбор метода)")
    print("="*60)
    
    steam_id = "76561198306528518"
    
    print(f"\n📥 Загружаем через SteamService.get_inventory()")
    
    items = await SteamService.get_inventory(steam_id)
    
    if items:
        print(f"\n✅ Успешно загружено {len(items)} предметов!")
        
        # Подсчет по редкости
        rarity_count = {}
        for item in items:
            rarity = item.get('rarity', 'Unknown')
            rarity_count[rarity] = rarity_count.get(rarity, 0) + 1
        
        print("\nРаспределение по редкости:")
        for rarity, count in sorted(rarity_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {rarity}: {count}")
    else:
        print("\n⚠️ Инвентарь пустой или недоступен")
    
    return items


async def test_with_cookies():
    """Тест авторизованного метода (требует cookies)"""
    print("\n" + "="*60)
    print("ТЕСТ 3: Авторизованный метод (с cookies)")
    print("="*60)
    
    print("\n⚠️ Этот тест требует Steam cookies!")
    print("Получи их из браузера: F12 → Application → Cookies → steamcommunity.com")
    print("\nПропускаем тест (нет cookies)...")
    
    # Раскомментируй и добавь свои cookies для теста:
    # steam_id = "76561198306528518"
    # session_id = "твой_sessionid"
    # steam_login_secure = "твой_steamLoginSecure"
    # 
    # items = await SteamAuthenticatedInventory.get_inventory_with_cookies(
    #     steam_id=steam_id,
    #     session_id=session_id,
    #     steam_login_secure=steam_login_secure
    # )
    # 
    # if items:
    #     print(f"\n✅ Загружено {len(items)} предметов через авторизованный метод!")
    # else:
    #     print("\n⚠️ Не удалось загрузить")


async def main():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ ЗАГРУЗКИ STEAM ИНВЕНТАРЯ")
    print("="*60)
    
    try:
        # Тест 1: Публичный метод
        await test_public_inventory()
        
        # Небольшая задержка между тестами
        await asyncio.sleep(2)
        
        # Тест 2: Основной сервис
        await test_main_service()
        
        # Тест 3: С cookies (пропускается без cookies)
        await test_with_cookies()
        
        print("\n" + "="*60)
        print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Запуск тестов
    asyncio.run(main())
