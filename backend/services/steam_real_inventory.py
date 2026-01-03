"""
Реальная загрузка Steam инвентаря (как у Lis-Skins)
"""
import requests
import time
import json
from typing import List, Dict


class SteamRealInventory:
    """Загрузчик реального Steam инвентаря"""
    
    @staticmethod
    def load_inventory(steam_id: str, retries: int = 3) -> List[Dict]:
        """
        Загрузить реальный CS2 инвентарь
        
        Использует метод как у Lis-Skins:
        - Правильные заголовки браузера
        - Задержки между запросами
        - Множественные попытки
        """
        
        for attempt in range(retries):
            print(f"[REAL_INV] Попытка {attempt + 1}/{retries} для {steam_id}")
            
            try:
                items = SteamRealInventory._fetch_inventory(steam_id)
                
                if items and len(items) > 0:
                    print(f"[REAL_INV] ✅ Загружено {len(items)} предметов")
                    return items
                
                # Если пусто, ждем и пробуем еще
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"[REAL_INV] Пусто, ждем {wait_time}с...")
                    time.sleep(wait_time)
                    
            except Exception as e:
                print(f"[REAL_INV] Ошибка попытки {attempt + 1}: {e}")
                
                if attempt < retries - 1:
                    time.sleep(2)
        
        print(f"[REAL_INV] ❌ Не удалось загрузить после {retries} попыток")
        return []
    
    @staticmethod
    def _fetch_inventory(steam_id: str) -> List[Dict]:
        """Один запрос к Steam API"""
        
        url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"
        
        # Заголовки как у реального браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': f'https://steamcommunity.com/profiles/{steam_id}/inventory',
            'Origin': 'https://steamcommunity.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        params = {
            'l': 'english'
            # Убрали count=5000 - Steam возвращает 400 с этим параметром
        }
        
        session = requests.Session()
        
        # Сначала заходим на страницу профиля чтобы получить cookies
        try:
            profile_url = f"https://steamcommunity.com/profiles/{steam_id}/inventory"
            session.get(profile_url, headers=headers, timeout=10)
            time.sleep(1)
        except:
            pass
        
        # Теперь запрашиваем инвентарь
        response = session.get(url, headers=headers, params=params, timeout=30)
        
        print(f"[REAL_INV] Status: {response.status_code}")
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")
        
        data = response.json()
        
        if not data.get('success'):
            error = data.get('Error', 'Unknown')
            raise Exception(f"Steam error: {error}")
        
        assets = data.get('assets', [])
        descriptions = data.get('descriptions', [])
        
        print(f"[REAL_INV] Assets: {len(assets)}, Descriptions: {len(descriptions)}")
        
        if len(assets) == 0:
            return []
        
        # Маппинг описаний
        desc_map = {}
        for desc in descriptions:
            key = f"{desc['classid']}_{desc['instanceid']}"
            desc_map[key] = desc
        
        items = []
        for asset in assets:
            key = f"{asset['classid']}_{asset['instanceid']}"
            desc = desc_map.get(key, {})
            
            # Только tradable предметы
            if desc.get('tradable') != 1:
                continue
            
            # Извлечь редкость
            rarity = None
            for tag in desc.get('tags', []):
                if tag.get('category') == 'Rarity':
                    rarity = tag.get('localized_tag_name') or tag.get('name')
                    break
            
            items.append({
                'assetid': asset['assetid'],
                'classid': asset['classid'],
                'instanceid': asset['instanceid'],
                'market_hash_name': desc.get('market_hash_name', ''),
                'name': desc.get('name', ''),
                'type': desc.get('type', ''),
                'icon_url': f"https://community.cloudflare.steamstatic.com/economy/image/{desc.get('icon_url', '')}",
                'rarity': rarity,
                'float_value': None,
                'amount': int(asset.get('amount', 1))
            })
        
        return items
