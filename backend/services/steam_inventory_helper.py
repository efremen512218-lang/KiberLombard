"""
Помощник для загрузки Steam инвентаря через различные методы
"""
import httpx
import asyncio
from typing import List, Dict, Optional
from services.steam_real_inventory import SteamRealInventory


class SteamInventoryHelper:
    """Загрузчик инвентаря с множественными fallback методами"""
    
    @staticmethod
    async def get_inventory_multi_method(steam_id: str) -> List[Dict]:
        """
        Попытка загрузить инвентарь через несколько методов
        """
        
        # Метод 1: Реальный загрузчик с cookies и задержками (как у Lis-Skins)
        print(f"[HELPER] Метод 1: Реальный загрузчик для {steam_id}")
        try:
            items = SteamRealInventory.load_inventory(steam_id, retries=3)
            if items and len(items) > 0:
                print(f"[HELPER] ✅ Метод 1 успешен: {len(items)} предметов")
                return items
        except Exception as e:
            print(f"[HELPER] Метод 1 ошибка: {e}")
        
        # Метод 2: Через Steam Bot (если запущен)
        print(f"[HELPER] Метод 2: Через Steam Bot для {steam_id}")
        items = await SteamInventoryHelper._method_bot(steam_id)
        if items:
            return items
        
        # Метод 3: Прямой запрос
        print(f"[HELPER] Метод 3: Прямой запрос для {steam_id}")
        items = await SteamInventoryHelper._method_direct(steam_id)
        if items:
            return items
        
        print(f"[HELPER] ❌ Все методы не сработали для {steam_id}")
        return []
    
    @staticmethod
    async def _method_direct(steam_id: str) -> List[Dict]:
        """Прямой запрос к Steam API"""
        url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f'https://steamcommunity.com/profiles/{steam_id}/inventory',
        }
        
        params = {'l': 'english'}  # Убрали count=5000 - Steam возвращает 400
        
        try:
            await asyncio.sleep(2)  # Задержка для избежания rate limit
            
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        return SteamInventoryHelper._parse_inventory(data)
        except Exception as e:
            print(f"[HELPER] Метод 1 ошибка: {e}")
        
        return []
    
    @staticmethod
    async def _method_alternative_headers(steam_id: str) -> List[Dict]:
        """Запрос с альтернативными заголовками"""
        url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"
        
        headers = {
            'User-Agent': 'Steam 1291812 / iPhone',
            'Accept': 'application/json',
        }
        
        params = {'l': 'english'}  # Убрали count=5000 - Steam возвращает 400
        
        try:
            await asyncio.sleep(2)
            
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        return SteamInventoryHelper._parse_inventory(data)
        except Exception as e:
            print(f"[HELPER] Метод 2 ошибка: {e}")
        
        return []
    
    @staticmethod
    async def _method_bot(steam_id: str) -> List[Dict]:
        """Загрузка через Steam Bot"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"http://localhost:3001/api/inventory/{steam_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        return data.get('items', [])
        except Exception as e:
            print(f"[HELPER] Метод 3 ошибка: {e}")
        
        return []
    
    @staticmethod
    def _parse_inventory(data: dict) -> List[Dict]:
        """Парсинг ответа Steam API"""
        assets = data.get('assets', [])
        descriptions = data.get('descriptions', [])
        
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
        
        return items
