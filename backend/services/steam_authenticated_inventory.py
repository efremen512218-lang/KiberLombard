"""
Загрузка инвентаря Steam с авторизацией через cookies
Метод работает как на Lis-Skins и других рабочих сервисах
"""
import httpx
import asyncio
from typing import List, Dict, Optional
import json


class SteamAuthenticatedInventory:
    """
    Загрузчик инвентаря с авторизацией через Steam cookies
    
    Этот метод работает даже для приватных инвентарей, если у вас есть
    правильные cookies от авторизованной сессии Steam.
    """
    
    @staticmethod
    async def get_inventory_with_cookies(
        steam_id: str,
        session_id: Optional[str] = None,
        steam_login_secure: Optional[str] = None,
        app_id: int = 730,
        context_id: int = 2
    ) -> List[Dict]:
        """
        Загрузить инвентарь с использованием Steam cookies
        
        Args:
            steam_id: Steam ID64 пользователя
            session_id: Cookie sessionid из Steam
            steam_login_secure: Cookie steamLoginSecure из Steam
            app_id: ID игры (730 = CS2)
            context_id: Контекст инвентаря (2 = основной)
        
        Returns:
            Список предметов инвентаря
        """
        url = f"https://steamcommunity.com/inventory/{steam_id}/{app_id}/{context_id}"
        
        # Заголовки как у настоящего браузера
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': f'https://steamcommunity.com/profiles/{steam_id}/inventory',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        }
        
        # Cookies для авторизации
        cookies = {}
        if session_id:
            cookies['sessionid'] = session_id
        if steam_login_secure:
            cookies['steamLoginSecure'] = steam_login_secure
        
        params = {
            'l': 'english'
            # Убрали count=5000 - Steam возвращает 400 с этим параметром
        }
        
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            try:
                # Задержка для избежания rate limit
                await asyncio.sleep(1)
                
                response = await client.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    params=params
                )
                
                print(f"[AUTH_INVENTORY] Status: {response.status_code} for {steam_id}")
                
                if response.status_code == 403:
                    print(f"[AUTH_INVENTORY] Доступ запрещен для {steam_id}")
                    return []
                
                if response.status_code == 429:
                    print(f"[AUTH_INVENTORY] Rate limit, ждем 5 секунд...")
                    await asyncio.sleep(5)
                    response = await client.get(url, headers=headers, cookies=cookies, params=params)
                
                if response.status_code != 200:
                    print(f"[AUTH_INVENTORY] Ошибка {response.status_code}: {response.text[:200]}")
                    return []
                
                data = response.json()
                
                if not data.get('success'):
                    error = data.get('Error', 'Unknown error')
                    print(f"[AUTH_INVENTORY] Steam error: {error}")
                    return []
                
                assets = data.get('assets', [])
                descriptions = data.get('descriptions', [])
                
                print(f"[AUTH_INVENTORY] Найдено {len(assets)} предметов")
                
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
                
                print(f"[AUTH_INVENTORY] Загружено {len(items)} tradable предметов")
                return items
                
            except Exception as e:
                print(f"[AUTH_INVENTORY] Ошибка: {e}")
                return []
    
    @staticmethod
    async def get_inventory_public(
        steam_id: str,
        app_id: int = 730,
        context_id: int = 2,
        retry_count: int = 3
    ) -> List[Dict]:
        """
        Загрузить публичный инвентарь без авторизации
        С улучшенной обработкой ошибок и retry логикой
        
        Args:
            steam_id: Steam ID64 пользователя
            app_id: ID игры (730 = CS2)
            context_id: Контекст инвентаря (2 = основной)
            retry_count: Количество попыток при ошибках
        
        Returns:
            Список предметов инвентаря
        """
        url = f"https://steamcommunity.com/inventory/{steam_id}/{app_id}/{context_id}"
        
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
        
        for attempt in range(retry_count):
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                try:
                    # Задержка между попытками
                    if attempt > 0:
                        wait_time = 2 ** attempt  # Exponential backoff
                        print(f"[PUBLIC_INVENTORY] Попытка {attempt + 1}/{retry_count}, ждем {wait_time}с...")
                        await asyncio.sleep(wait_time)
                    else:
                        await asyncio.sleep(1)
                    
                    response = await client.get(url, headers=headers, params=params)
                    
                    print(f"[PUBLIC_INVENTORY] Status: {response.status_code} for {steam_id}")
                    
                    # Обработка различных статусов
                    if response.status_code == 403:
                        print(f"[PUBLIC_INVENTORY] Инвентарь приватный")
                        return []
                    
                    if response.status_code == 429:
                        print(f"[PUBLIC_INVENTORY] Rate limit")
                        if attempt < retry_count - 1:
                            continue
                        return []
                    
                    if response.status_code == 500:
                        print(f"[PUBLIC_INVENTORY] Ошибка сервера Steam")
                        if attempt < retry_count - 1:
                            continue
                        return []
                    
                    if response.status_code != 200:
                        print(f"[PUBLIC_INVENTORY] Неожиданный статус: {response.status_code}")
                        if attempt < retry_count - 1:
                            continue
                        return []
                    
                    data = response.json()
                    
                    if not data.get('success'):
                        error = data.get('Error', 'Unknown error')
                        print(f"[PUBLIC_INVENTORY] Steam error: {error}")
                        
                        # Некоторые ошибки можно retry
                        if 'timeout' in error.lower() or 'busy' in error.lower():
                            if attempt < retry_count - 1:
                                continue
                        
                        return []
                    
                    assets = data.get('assets', [])
                    descriptions = data.get('descriptions', [])
                    
                    print(f"[PUBLIC_INVENTORY] Найдено {len(assets)} предметов")
                    
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
                    
                    print(f"[PUBLIC_INVENTORY] ✅ Загружено {len(items)} tradable предметов")
                    return items
                    
                except httpx.TimeoutException:
                    print(f"[PUBLIC_INVENTORY] Timeout на попытке {attempt + 1}")
                    if attempt < retry_count - 1:
                        continue
                    return []
                    
                except Exception as e:
                    print(f"[PUBLIC_INVENTORY] Ошибка на попытке {attempt + 1}: {e}")
                    if attempt < retry_count - 1:
                        continue
                    return []
        
        return []
    
    @staticmethod
    def extract_cookies_from_browser_string(cookie_string: str) -> Dict[str, str]:
        """
        Извлечь cookies из строки браузера
        
        Формат: "sessionid=xxx; steamLoginSecure=yyy"
        
        Args:
            cookie_string: Строка с cookies из браузера
        
        Returns:
            Словарь с cookies
        """
        cookies = {}
        
        for cookie in cookie_string.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies[key.strip()] = value.strip()
        
        return cookies
