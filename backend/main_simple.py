from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from typing import List
import random

app = FastAPI(
    title="КиберЛомбард CS2 API (Demo)",
    description="Demo API с mock данными",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock данные
MOCK_ITEMS = [
    {
        "assetid": "1",
        "market_hash_name": "AK-47 | Redline (Field-Tested)",
        "name": "AK-47 | Redline",
        "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot7HxfDhjxszJemkV09-5lpKKqPrxN7LEmyVQ7MEpiLuSrYmnjQO3-UdsZGHyd4_Bd1RvNQ7T_FDrw-_ng5Pu75iY1zI97bhxLJYm/360fx360f",
        "type": "Rifle",
        "rarity": "Classified",
        "market_price": 850.50
    },
    {
        "assetid": "2",
        "market_hash_name": "AWP | Asiimov (Field-Tested)",
        "name": "AWP | Asiimov",
        "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpot621FAR17PLfYQJD_9W7m5a0mvLwOq7c2D4D6sQl2LqQo9-g2wHh-kU5Yzv3JoKRdQE2YVqE_1K9xOjxxcjrYPCSpA/360fx360f",
        "type": "Sniper Rifle",
        "rarity": "Covert",
        "market_price": 4250.00
    },
    {
        "assetid": "3",
        "market_hash_name": "M4A4 | Howl (Field-Tested)",
        "name": "M4A4 | Howl",
        "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpou-6kejhz2v_Nfz5H_uO1gb-Gw_alIITSl3lU18l4jeHVyoD0mlOx5UprZWGhJoWWdgE4YFnU_1K9xOjxxcjrYPCSpA/360fx360f",
        "type": "Rifle",
        "rarity": "Contraband",
        "market_price": 125000.00
    },
    {
        "assetid": "4",
        "market_hash_name": "Glock-18 | Fade (Factory New)",
        "name": "Glock-18 | Fade",
        "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgposbaqKAxf0Ob3djFN79fnzL-YkvbnNrfummRD7fp9g-7J4bP5iUazrl1qZmD1JoSQdQE-YV3V_1K9xOjxxcjrYPCSpA/360fx360f",
        "type": "Pistol",
        "rarity": "Restricted",
        "market_price": 1850.00
    },
    {
        "assetid": "5",
        "market_hash_name": "Desert Eagle | Blaze (Factory New)",
        "name": "Desert Eagle | Blaze",
        "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgposr-kLAtl7PLZTjlH_9mkgIWKkPvLPr7Vn35cppQg3L2Xo9-g2wHh-kU5Yzv3JoKRdQE2YVqE_1K9xOjxxcjrYPCSpA/360fx360f",
        "type": "Pistol",
        "rarity": "Restricted",
        "market_price": 2100.00
    },
    {
        "assetid": "6",
        "market_hash_name": "Karambit | Fade (Factory New)",
        "name": "★ Karambit | Fade",
        "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpovbSsLQJf2PLacDBA5ciJlY20k_jkI7fUhFRd4cJ5nqeQpN-g2wHh-kU5Yzv3JoKRdQE2YVqE_1K9xOjxxcjrYPCSpA/360fx360f",
        "type": "Knife",
        "rarity": "Covert",
        "market_price": 185000.00
    },
    {
        "assetid": "7",
        "market_hash_name": "USP-S | Kill Confirmed (Minimal Wear)",
        "name": "USP-S | Kill Confirmed",
        "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpoo6m1FBRp3_bGcjhQ09-jq5WYh8j_OrfdqWdQ-sJ0teXI8oThxlCx-kU5Yzv3JoKRdQE2YVqE_1K9xOjxxcjrYPCSpA/360fx360f",
        "type": "Pistol",
        "rarity": "Classified",
        "market_price": 3200.00
    },
    {
        "assetid": "8",
        "market_hash_name": "P250 | Asiimov (Field-Tested)",
        "name": "P250 | Asiimov",
        "icon_url": "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQknCRvCo04DEVlxkKgpopujwezhjxszYI2gS09-5lpKKqPrxN7LEmyVQ7MEpiLuSrYmnjQO3-UdsZGHyd4_Bd1RvNQ7T_FDrw-_ng5Pu75iY1zI97bhxLJYm/360fx360f",
        "type": "Pistol",
        "rarity": "Classified",
        "market_price": 450.00
    }
]

MOCK_DEALS = []

# ============= ENDPOINTS =============

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "mode": "demo",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/auth/steam/verify")
async def verify_steam_user(steam_id: str):
    """Mock верификация Steam пользователя"""
    return {
        "id": 1,
        "steam_id": steam_id,
        "steam_username": "Demo User",
        "steam_avatar": "https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg",
        "phone": None,
        "phone_verified": False,
        "passport_verified": False,
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/inventory/{steam_id}")
async def get_inventory(steam_id: str):
    """
    Получить инвентарь CS2
    Сначала пытается загрузить реальный через Steam API,
    если не получается - возвращает mock данные
    """
    
    # Попытка загрузить реальный инвентарь
    # Для этого нужен Steam API ключ в переменной окружения STEAM_API_KEY
    import os
    steam_api_key = os.getenv('STEAM_API_KEY', '')
    
    if steam_api_key:
        try:
            # Загрузка реального инвентаря через Steam API
            import httpx
            
            url = "https://steamcommunity.com/inventory/{}/730/2".format(steam_id)
            params = {"l": "english", "count": 5000}
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and data.get("assets"):
                        # Парсинг реального инвентаря
                        assets = data.get("assets", [])
                        descriptions = data.get("descriptions", [])
                        
                        # Создаем маппинг описаний
                        desc_map = {}
                        for desc in descriptions:
                            key = f"{desc['classid']}_{desc['instanceid']}"
                            desc_map[key] = desc
                        
                        items = []
                        total_value = 0
                        
                        for asset in assets[:50]:  # Ограничим 50 предметами для демо
                            key = f"{asset['classid']}_{asset['instanceid']}"
                            desc = desc_map.get(key, {})
                            
                            if desc.get("tradable") == 1:
                                # Примерная цена (в реальности нужен API маркетов)
                                price = random.uniform(100, 5000)
                                
                                items.append({
                                    "assetid": asset["assetid"],
                                    "market_hash_name": desc.get("market_hash_name", "Unknown"),
                                    "name": desc.get("name", "Unknown"),
                                    "icon_url": f"https://community.cloudflare.steamstatic.com/economy/image/{desc.get('icon_url', '')}",
                                    "type": desc.get("type", ""),
                                    "rarity": extract_rarity(desc.get("tags", [])),
                                    "market_price": round(price, 2)
                                })
                                total_value += price
                        
                        if items:
                            return {
                                "steam_id": steam_id,
                                "items": items,
                                "total_value": round(total_value, 2),
                                "last_updated": datetime.utcnow().isoformat(),
                                "source": "steam_api"
                            }
        except Exception as e:
            print(f"Error loading real inventory: {e}")
    
    # Fallback на mock данные
    total_value = sum(item["market_price"] for item in MOCK_ITEMS)
    
    return {
        "steam_id": steam_id,
        "items": MOCK_ITEMS,
        "total_value": total_value,
        "last_updated": datetime.utcnow().isoformat(),
        "source": "mock"
    }

def extract_rarity(tags):
    """Извлечь редкость из тегов"""
    for tag in tags:
        if tag.get("category") == "Rarity":
            return tag.get("localized_tag_name")
    return None

@app.post("/api/quote")
async def calculate_quote(data: dict):
    """Расчет условий сделки"""
    asset_ids = data.get("asset_ids", [])
    option_days = data.get("option_days", 14)
    
    selected_items = [item for item in MOCK_ITEMS if item["assetid"] in asset_ids]
    market_total = sum(item["market_price"] for item in selected_items)
    
    loan_amount = market_total * 0.65
    buyback_price = market_total * 1.15 + loan_amount * 0.25
    option_expiry = datetime.utcnow() + timedelta(days=option_days)
    
    return {
        "market_total": round(market_total, 2),
        "loan_amount": round(loan_amount, 2),
        "buyback_price": round(buyback_price, 2),
        "option_expiry": option_expiry.isoformat(),
        "items": selected_items,
        "breakdown": {
            "market_total": round(market_total, 2),
            "loan_percentage": "65%",
            "loan_amount": round(loan_amount, 2),
            "buyback_base": round(market_total * 1.15, 2),
            "option_premium": round(loan_amount * 0.25, 2),
            "buyback_total": round(buyback_price, 2),
            "option_days": option_days,
            "option_expiry": option_expiry.isoformat()
        }
    }

@app.post("/api/kyc/phone/send-code")
async def send_phone_code(phone: str):
    """Mock отправка SMS"""
    code = str(random.randint(100000, 999999))
    return {
        "success": True,
        "message": "SMS-код отправлен",
        "dev_code": code
    }

@app.post("/api/kyc/phone/verify")
async def verify_phone(data: dict):
    """Mock верификация телефона"""
    return {
        "success": True,
        "message": "Телефон подтвержден"
    }

@app.post("/api/deals")
async def create_deal(data: dict):
    """Создание сделки"""
    deal_id = len(MOCK_DEALS) + 1
    
    quote_request = data.get("quote_request", {})
    asset_ids = quote_request.get("asset_ids", [])
    option_days = quote_request.get("option_days", 14)
    
    selected_items = [item for item in MOCK_ITEMS if item["assetid"] in asset_ids]
    market_total = sum(item["market_price"] for item in selected_items)
    
    loan_amount = market_total * 0.65
    buyback_price = market_total * 1.15 + loan_amount * 0.25
    option_expiry = datetime.utcnow() + timedelta(days=option_days)
    
    deal = {
        "id": deal_id,
        "user_id": 1,
        "market_total": round(market_total, 2),
        "loan_amount": round(loan_amount, 2),
        "buyback_price": round(buyback_price, 2),
        "created_at": datetime.utcnow().isoformat(),
        "option_expiry": option_expiry.isoformat(),
        "deal_status": "ACTIVE",
        "items_snapshot": selected_items,
        "initial_trade_url": "https://steamcommunity.com/tradeoffer/new/?partner=123456789&token=DEMO",
        "contract_pdf_url": f"/contracts/deal_{deal_id}.pdf"
    }
    
    MOCK_DEALS.append(deal)
    
    return deal

@app.get("/api/deals")
async def get_deals(steam_id: str):
    """Получить сделки пользователя"""
    return MOCK_DEALS

@app.get("/api/deals/{deal_id}")
async def get_deal(deal_id: int):
    """Получить детали сделки"""
    deal = next((d for d in MOCK_DEALS if d["id"] == deal_id), None)
    
    if not deal:
        # Создаем демо сделку если не найдена
        deal = {
            "id": deal_id,
            "user_id": 1,
            "market_total": 10000.00,
            "loan_amount": 6500.00,
            "buyback_price": 13125.00,
            "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
            "option_expiry": (datetime.utcnow() + timedelta(days=9)).isoformat(),
            "deal_status": "ACTIVE",
            "items_snapshot": MOCK_ITEMS[:3],
            "initial_trade_url": "https://steamcommunity.com/tradeoffer/new/?partner=123456789&token=DEMO",
            "contract_pdf_url": f"/contracts/deal_{deal_id}.pdf",
            "is_expired": False,
            "can_buyback": True,
            "days_left": 9
        }
    
    return deal

@app.post("/api/deals/{deal_id}/buyback")
async def buyback_deal(deal_id: int, data: dict):
    """Выкуп сделки"""
    return {
        "success": True,
        "message": "Выкуп оформлен, ожидайте трейд",
        "trade_url": "https://steamcommunity.com/tradeoffer/new/?partner=123456789&token=DEMO"
    }

@app.get("/api/stats/public")
async def get_public_stats():
    """Публичная статистика"""
    return {
        "total_deals": 1247,
        "active_deals": 89,
        "total_volume": 15750000.00,
        "avg_deal_amount": 12630.00,
        "buyback_rate": 67.5
    }

@app.post("/api/calculator")
async def calculator(data: dict):
    """Калькулятор"""
    market_price = data.get("market_price", 0)
    option_days = data.get("option_days", 14)
    
    loan_amount = market_price * 0.65
    buyback_price = market_price * 1.15 + loan_amount * 0.25
    option_expiry = datetime.utcnow() + timedelta(days=option_days)
    
    return {
        "market_total": round(market_price, 2),
        "loan_amount": round(loan_amount, 2),
        "buyback_price": round(buyback_price, 2),
        "option_expiry": option_expiry.isoformat(),
        "breakdown": {
            "market_total": round(market_price, 2),
            "loan_percentage": "65%",
            "loan_amount": round(loan_amount, 2),
            "buyback_base": round(market_price * 1.15, 2),
            "option_premium": round(loan_amount * 0.25, 2),
            "buyback_total": round(buyback_price, 2),
            "option_days": option_days
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск КиберЛомбард CS2 API (Demo Mode)")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
