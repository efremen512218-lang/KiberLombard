"""
Тест загрузки реального инвентаря
"""
import requests
import json

steam_id = "76561198306528518"
url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
}

params = {
    'l': 'english',
    'count': 5000
}

print(f"Загружаем инвентарь для {steam_id}...")
print(f"URL: {url}")
print(f"Params: {params}")

# Попробуем сначала без параметров
print("\n=== Попытка 1: Без параметров ===")
try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Assets: {len(data.get('assets', []))}")
        print(f"Descriptions: {len(data.get('descriptions', []))}")
        
        assets = data.get('assets', [])
        if assets:
            print(f"\n✅ Найдено {len(assets)} предметов без параметров!")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Попробуем с параметрами
print("\n=== Попытка 2: С параметрами ===")
try:
    response = requests.get(url, headers=headers, params=params, timeout=30)
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Assets: {len(data.get('assets', []))}")
        print(f"Descriptions: {len(data.get('descriptions', []))}")
        print(f"Total inventory count: {data.get('total_inventory_count', 0)}")
        
        if data.get('Error'):
            print(f"Error: {data.get('Error')}")
        
        assets = data.get('assets', [])
        descriptions = data.get('descriptions', [])
        
        if assets:
            print(f"\n✅ Найдено {len(assets)} предметов!")
            print("\nПервые 3 предмета:")
            
            # Создаем маппинг описаний
            desc_map = {}
            for desc in descriptions:
                key = f"{desc['classid']}_{desc['instanceid']}"
                desc_map[key] = desc
            
            for i, asset in enumerate(assets[:3], 1):
                key = f"{asset['classid']}_{asset['instanceid']}"
                desc = desc_map.get(key, {})
                print(f"{i}. {desc.get('name', 'Unknown')} - tradable: {desc.get('tradable', 0)}")
        else:
            print("\n⚠️ Нет предметов в инвентаре")
            print("\nПолный ответ:")
            print(json.dumps(data, indent=2)[:500])
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc()
