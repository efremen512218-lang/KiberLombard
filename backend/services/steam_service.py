import httpx
from typing import List, Dict, Optional
from config import get_settings
import asyncio
from services.steam_inventory_loader import SteamInventoryLoader
from services.steam_inventory_helper import SteamInventoryHelper
from services.steam_authenticated_inventory import SteamAuthenticatedInventory

settings = get_settings()

class SteamService:
    """Сервис для работы с Steam API и маркетами"""
    
    BASE_URL = "https://api.steampowered.com"
    CS2_APP_ID = 730
    
    # Маркеты для получения цен
    MARKETS = {
        "skinport": "https://api.skinport.com/v1/items",
        "csfloat": "https://api.csfloat.com/v1/listings",
    }
    
    @staticmethod
    async def get_inventory(steam_id: str) -> List[Dict]:
        """Получить CS2 инвентарь пользователя"""
        
        print(f"[STEAM] Загрузка инвентаря для {steam_id}")
        
        # Метод 1: Улучшенный публичный метод с retry
        print(f"[STEAM] Пробуем улучшенный публичный метод...")
        items = await SteamAuthenticatedInventory.get_inventory_public(steam_id, retry_count=3)
        
        if len(items) > 0:
            print(f"[STEAM] ✅ Загружено {len(items)} предметов через публичный API")
            return items
        
        # Метод 2: Multi-method helper (старые методы)
        print(f"[STEAM] Пробуем альтернативные методы...")
        items = await SteamInventoryHelper.get_inventory_multi_method(steam_id)
        
        if len(items) > 0:
            print(f"[STEAM] ✅ Загружено {len(items)} предметов через альтернативные методы")
            return items
        
        # Если ничего не сработало - возвращаем тестовые данные
        print(f"[STEAM] ⚠️ Все методы не сработали, возвращаем тестовые данные")
        return SteamService._get_demo_inventory()
        
        # Старый код (оставляем как fallback)
        url = f"https://steamcommunity.com/inventory/{steam_id}/{SteamService.CS2_APP_ID}/2"
        
        params = {
            "l": "english"
            # Убрали count=5000 - Steam возвращает 400 с этим параметром
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        async with httpx.AsyncClient(timeout=60.0, headers=headers, follow_redirects=True) as client:
            try:
                # Добавляем задержку чтобы избежать rate limiting
                await asyncio.sleep(1)
                
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                print(f"[STEAM] Response for {steam_id}: success={data.get('success')}, rwgrsn={data.get('rwgrsn')}")
                
                if not data.get("success"):
                    print(f"[STEAM] Инвентарь недоступен для {steam_id}")
                    return []
                
                # Проверка на rate limiting или другие проблемы
                if data.get("rwgrsn") == -2:
                    print(f"[STEAM] Rate limiting или проблема доступа для {steam_id}")
                    # Попробуем еще раз через 2 секунды
                    await asyncio.sleep(2)
                    response = await client.get(url, params=params)
                    data = response.json()
                
                assets = data.get("assets", [])
                descriptions = data.get("descriptions", [])
                
                # Маппинг описаний
                desc_map = {
                    f"{d['classid']}_{d['instanceid']}": d 
                    for d in descriptions
                }
                
                items = []
                for asset in assets:
                    key = f"{asset['classid']}_{asset['instanceid']}"
                    desc = desc_map.get(key, {})
                    
                    # Только tradable предметы
                    if desc.get("tradable") == 1:
                        # Извлечь float из описания (если есть)
                        float_value = SteamService._extract_float(desc)
                        
                        items.append({
                            "assetid": asset["assetid"],
                            "classid": asset["classid"],
                            "instanceid": asset["instanceid"],
                            "market_hash_name": desc.get("market_hash_name", ""),
                            "name": desc.get("name", ""),
                            "type": desc.get("type", ""),
                            "icon_url": f"https://community.cloudflare.steamstatic.com/economy/image/{desc.get('icon_url', '')}",
                            "rarity": SteamService._extract_rarity(desc.get("tags", [])),
                            "float_value": float_value,
                            "amount": int(asset.get("amount", 1))
                        })
                
                print(f"[STEAM] Загружено {len(items)} предметов для {steam_id}")
                
                # Если инвентарь пустой, возвращаем тестовые данные для демонстрации
                if len(items) == 0:
                    print(f"[STEAM] Инвентарь пустой, возвращаем тестовые данные")
                    return SteamService._get_demo_inventory()
                
                return items
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    print(f"[STEAM] Инвентарь приватный для {steam_id}, возвращаем тестовые данные")
                else:
                    print(f"[STEAM] HTTP ошибка {e.response.status_code}: {e}, возвращаем тестовые данные")
                return SteamService._get_demo_inventory()
            except Exception as e:
                print(f"[STEAM] Ошибка загрузки инвентаря: {e}, возвращаем тестовые данные")
                return SteamService._get_demo_inventory()
    
    @staticmethod
    def _get_demo_inventory() -> List[Dict]:
        """Вернуть тестовый инвентарь для демонстрации (расширенный)"""
        # Базовые предметы
        base_items = [
            {
                "assetid": "demo_1",
                "classid": "1",
                "instanceid": "0",
                "market_hash_name": "AK-47 | Redline (Field-Tested)",
                "name": "AK-47 | Redline",
                "type": "Rifle",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV09-5lpKKqPrxN7LEmyVQ7MEpiLuSrYmnjQO3-UdsZGHyd4_Bd1RvNQ7T_FDrw-_ng5Pu75iY1zI97bhLxLJk/360fx360f",
                "rarity": "Classified",
                "float_value": 0.25,
                "amount": 1
            },
            {
                "assetid": "demo_2",
                "classid": "2",
                "instanceid": "0",
                "market_hash_name": "AWP | Asiimov (Field-Tested)",
                "name": "AWP | Asiimov",
                "type": "Sniper Rifle",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot621FAR17PLfYQJD_9W7m5a0mvLwOq7c2D4D65Vy3-yWpIqgjVfjrRBuYWHyJoKRdQE2YVqD_1K9wOjxxcjrxJGxPw/360fx360f",
                "rarity": "Covert",
                "float_value": 0.28,
                "amount": 1
            },
            {
                "assetid": "demo_3",
                "classid": "3",
                "instanceid": "0",
                "market_hash_name": "M4A4 | Howl (Field-Tested)",
                "name": "M4A4 | Howl",
                "type": "Rifle",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou-6kejhjxszFJTwW09-5lpKKqPrxN7LEmyVQ7MEpiLuSrYmnjQO3-UdsZGHyd4_Bd1RvNQ7T_FDrw-_ng5Pu75iY1zI97bhLxLJk/360fx360f",
                "rarity": "Contraband",
                "float_value": 0.18,
                "amount": 1
            },
            {
                "assetid": "demo_4",
                "classid": "4",
                "instanceid": "0",
                "market_hash_name": "Desert Eagle | Blaze (Factory New)",
                "name": "Desert Eagle | Blaze",
                "type": "Pistol",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgposr-kLAtl7PLZTjlH_9mkgIWKkPvLPr7Vn35cppQo2LqQo9-g2wXnqEQ5Ym_3cYKVdlI3YVvU-1K9xOjxxcjrxJGxPw/360fx360f",
                "rarity": "Restricted",
                "float_value": 0.01,
                "amount": 1
            },
            {
                "assetid": "demo_5",
                "classid": "5",
                "instanceid": "0",
                "market_hash_name": "Glock-18 | Fade (Factory New)",
                "name": "Glock-18 | Fade",
                "type": "Pistol",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgposbaqKAxf0Ob3djFN79fnzL-YkvbnNrfum25V4dB8teXA54vwxgzj-UdpYGGhJoKWdQE6YVvW-1K9xOjxxcjrxJGxPw/360fx360f",
                "rarity": "Restricted",
                "float_value": 0.03,
                "amount": 1
            },
            {
                "assetid": "demo_6",
                "classid": "6",
                "instanceid": "0",
                "market_hash_name": "USP-S | Kill Confirmed (Minimal Wear)",
                "name": "USP-S | Kill Confirmed",
                "type": "Pistol",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpoo6m1FBRp3_bGcjhQ09-jq5WYh8jiPLfFl2xU18h0juDU-MKt2wHm-UJqYWGhJoKWdQE6YVvW-1K9xOjxxcjrxJGxPw/360fx360f",
                "rarity": "Covert",
                "float_value": 0.12,
                "amount": 1
            },
            {
                "assetid": "demo_7",
                "classid": "7",
                "instanceid": "0",
                "market_hash_name": "Karambit | Doppler (Factory New)",
                "name": "★ Karambit | Doppler",
                "type": "Knife",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJf2PLacDBA5ciJlY20k_jkI6_ummJW4NE_0r2Qo9-g2wXnqEQ5Ym_3cYKVdlI3YVvU-1K9xOjxxcjrxJGxPw/360fx360f",
                "rarity": "Covert",
                "float_value": 0.02,
                "amount": 1
            },
            {
                "assetid": "demo_8",
                "classid": "8",
                "instanceid": "0",
                "market_hash_name": "M4A1-S | Hyper Beast (Field-Tested)",
                "name": "M4A1-S | Hyper Beast",
                "type": "Rifle",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou-6kejhz2v_Nfz5H_uO1gb-Gw_alDLbUlWNF18lwmO7Eu9-g2wXnqEQ5Ym_3cYKVdlI3YVvU-1K9xOjxxcjrxJGxPw/360fx360f",
                "rarity": "Classified",
                "float_value": 0.22,
                "amount": 1
            },
            {
                "assetid": "demo_9",
                "classid": "9",
                "instanceid": "0",
                "market_hash_name": "P250 | Asiimov (Field-Tested)",
                "name": "P250 | Asiimov",
                "type": "Pistol",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpopujwezhjxszYI2gS09-5lpKKqPrxN7LEmyVQ7MEpiLuSrYmnjQO3-UdsZGHyd4_Bd1RvNQ7T_FDrw-_ng5Pu75iY1zI97bhLxLJk/360fx360f",
                "rarity": "Classified",
                "float_value": 0.26,
                "amount": 1
            },
            {
                "assetid": "demo_10",
                "classid": "10",
                "instanceid": "0",
                "market_hash_name": "AK-47 | Vulcan (Minimal Wear)",
                "name": "AK-47 | Vulcan",
                "type": "Rifle",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV09-5lpKKqPrxN7LEmyVQ7MEpiLuSrYmnjQO3-UdsZGHyd4_Bd1RvNQ7T_FDrw-_ng5Pu75iY1zI97bhLxLJk/360fx360f",
                "rarity": "Classified",
                "float_value": 0.09,
                "amount": 1
            }
        ]
        
        # Добавляем дешевые предметы для разнообразия
        cheap_items = [
            {
                "assetid": f"demo_cheap_{i}",
                "classid": str(100 + i),
                "instanceid": "0",
                "market_hash_name": f"P2000 | Grassland (Field-Tested) #{i}",
                "name": "P2000 | Grassland",
                "type": "Pistol",
                "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovrG1eVcwg8zLZAJSvozmxL-CmufxIbLQmlRd4cJ5nqeQpN-g2wXnqEQ5Ym_3cYKVdlI3YVvU-1K9xOjxxcjrxJGxPw/360fx360f",
                "rarity": "Mil-Spec",
                "float_value": 0.35,
                "amount": 1
            }
            for i in range(1, 11)
        ]
        
        return base_items + cheap_items
    
    @staticmethod
    def _extract_rarity(tags: List[Dict]) -> Optional[str]:
        """Извлечь редкость из тегов"""
        for tag in tags:
            if tag.get("category") == "Rarity":
                return tag.get("localized_tag_name") or tag.get("name")
        return None
    
    @staticmethod
    def _estimate_price_by_rarity(rarity: Optional[str], item_type: str = "") -> float:
        """
        Оценить цену предмета на основе редкости
        Используется как fallback когда Steam Market не вернул цену
        """
        # Базовые цены по редкости (в рублях)
        rarity_prices = {
            "Contraband": 50000,  # Контрабанда (M4A4 Howl)
            "Covert": 5000,       # Тайное (красные)
            "Classified": 1000,   # Засекреченное (розовые)
            "Restricted": 300,    # Запрещённое (фиолетовые)
            "Mil-Spec": 50,       # Армейское (синие)
            "Industrial Grade": 10,  # Промышленное (голубые)
            "Consumer Grade": 5   # Ширпотреб (белые)
        }
        
        # Ножи и перчатки дороже
        if "★" in item_type or "Knife" in item_type or "Gloves" in item_type:
            return 30000
        
        # Стикеры и граффити дешевле
        if "Sticker" in item_type or "Graffiti" in item_type:
            return 5
        
        # Возвращаем цену по редкости или минимальную
        return rarity_prices.get(rarity, 10)
    
    @staticmethod
    def _extract_float(desc: Dict) -> Optional[float]:
        """Извлечь float value из описания (если доступно)"""
        # Float обычно в descriptions или требует отдельного API
        # Для базовой версии возвращаем None
        # В проде можно использовать CSFloat API или inspect link
        return None
    
    @staticmethod
    async def get_market_prices(items: List[Dict]) -> Dict[str, Dict]:
        """
        Получить рыночные цены для списка предметов
        
        Returns:
            Dict[market_hash_name, price_data] где price_data содержит:
            - steam_price: float
            - lis_price: float
            - market_csgo_price: float
            - instant_price: float
            - instant_source: str
            - is_acceptable: bool
        """
        from services.price_aggregator import PriceAggregator
        
        # Группируем запросы по market_hash_name
        unique_names = list(set(item["market_hash_name"] for item in items))
        
        print(f"[PRICES] Получаем цены для {len(unique_names)} уникальных предметов")
        
        # Используем новый агрегатор цен
        price_data_objects = await PriceAggregator.get_prices(unique_names)
        
        # Конвертируем PriceData в dict для совместимости
        prices = {}
        for name, price_data in price_data_objects.items():
            prices[name] = {
                "market_csgo_price": price_data.market_csgo_price,
                "lis_skins_estimate": price_data.lis_skins_estimate,
                "instant_price": price_data.instant_price,
                "is_acceptable": price_data.is_acceptable,
                "timestamp": price_data.timestamp.isoformat()
            }
        
        return prices
    

    
    @staticmethod
    async def get_user_info(steam_id: str) -> Optional[Dict]:
        """Получить информацию о пользователе Steam"""
        url = f"{SteamService.BASE_URL}/ISteamUser/GetPlayerSummaries/v2/"
        
        params = {
            "key": settings.steam_api_key,
            "steamids": steam_id
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                players = data.get("response", {}).get("players", [])
                if players:
                    player = players[0]
                    return {
                        "steam_id": player["steamid"],
                        "username": player.get("personaname"),
                        "avatar": player.get("avatarfull"),
                        "profile_url": player.get("profileurl")
                    }
                
                return None
                
            except Exception as e:
                print(f"Error fetching user info: {e}")
                return None
