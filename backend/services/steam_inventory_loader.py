"""
Альтернативный загрузчик инвентаря Steam через requests с эмуляцией браузера
"""
import requests
import time
from typing import List, Dict, Optional


class SteamInventoryLoader:
    """Загрузчик инвентаря Steam с эмуляцией браузера"""
    
    @staticmethod
    def get_inventory(steam_id: str, app_id: int = 730, context_id: int = 2) -> List[Dict]:
        """
        Загрузить инвентарь пользователя
        
        Args:
            steam_id: Steam ID64 пользователя
            app_id: ID игры (730 = CS2)
            context_id: Контекст инвентаря (2 = основной)
        
        Returns:
            Список предметов
        """
        url = f"https://steamcommunity.com/inventory/{steam_id}/{app_id}/{context_id}"
        
        # Эмулируем браузер
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': f'https://steamcommunity.com/profiles/{steam_id}/inventory',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        
        params = {
            'l': 'english'
            # Убрали count=5000 - Steam возвращает 400 с этим параметром
        }
        
        try:
            # Добавляем задержку чтобы не попасть в rate limit
            time.sleep(1)
            
            session = requests.Session()
            response = session.get(url, headers=headers, params=params, timeout=30)
            
            print(f"[INVENTORY] Status: {response.status_code} for {steam_id}")
            
            if response.status_code == 403:
                print(f"[INVENTORY] Инвентарь приватный для {steam_id}")
                raise Exception("PRIVATE_INVENTORY: Инвентарь закрыт. Откройте настройки приватности Steam.")
            
            if response.status_code == 400:
                print(f"[INVENTORY] Неверный запрос для {steam_id}")
                raise Exception("INVALID_REQUEST: Неверный Steam ID или инвентарь недоступен.")
            
            if response.status_code != 200:
                print(f"[INVENTORY] Error: {response.status_code} - {response.text[:200]}")
                raise Exception(f"STEAM_ERROR: Ошибка Steam API ({response.status_code})")
            
            data = response.json()
            
            if not data.get('success'):
                error_msg = data.get('Error', 'Unknown error')
                print(f"[INVENTORY] Not successful: {data}")
                raise Exception(f"STEAM_ERROR: {error_msg}")
            
            assets = data.get('assets', [])
            descriptions = data.get('descriptions', [])
            
            print(f"[INVENTORY] Found {len(assets)} assets, {len(descriptions)} descriptions")
            
            # Создаем маппинг описаний
            desc_map = {}
            for desc in descriptions:
                key = f"{desc['classid']}_{desc['instanceid']}"
                desc_map[key] = desc
            
            items = []
            for asset in assets:
                key = f"{asset['classid']}_{asset['instanceid']}"
                desc = desc_map.get(key, {})
                
                # Только tradable предметы
                if desc.get('tradable') == 1:
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
            
            print(f"[INVENTORY] Loaded {len(items)} tradable items")
            return items
            
        except requests.exceptions.RequestException as e:
            print(f"[INVENTORY] Request error: {e}")
            return []
        except Exception as e:
            print(f"[INVENTORY] Error: {e}")
            return []
