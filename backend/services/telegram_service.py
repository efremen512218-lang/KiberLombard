"""
Telegram уведомления для админов
"""

import httpx
import os
from typing import Optional

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_IDS = os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")
SITE_URL = os.getenv("SITE_URL", "http://localhost:3000")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def send_telegram_message(chat_id: str, text: str, reply_markup: dict = None) -> bool:
    """Отправить сообщение в Telegram"""
    if not BOT_TOKEN:
        print(f"[TG] No token, skip: {text[:50]}...")
        return False
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            import json
            payload["reply_markup"] = json.dumps(reply_markup)
        
        try:
            response = await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"[TG] Error: {e}")
            return False


async def notify_new_deal(deal_id: int, loan_amount: float, items_count: int, 
                          user_name: str = "Клиент", phone: str = "Не указан"):
    """Уведомить админов о новой сделке"""
    
    text = f"""
🆕 <b>Новая сделка #{deal_id}</b>

👤 Клиент: {user_name}
📱 Телефон: {phone}
🎮 Скинов: {items_count}
💰 Сумма: {loan_amount:,.0f} ₽

⏳ Ожидает трейда

🔗 <a href="{SITE_URL}/admin">Админка</a>
"""
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Принять", "callback_data": f"accept_{deal_id}"},
                {"text": "❌ Отклонить", "callback_data": f"reject_{deal_id}"}
            ],
            [{"text": "👁️ Подробнее", "url": f"{SITE_URL}/cabinet/deals/{deal_id}"}]
        ]
    }
    
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await send_telegram_message(admin_id.strip(), text, keyboard)


async def notify_trade_accepted(deal_id: int, payout_amount: float):
    """Уведомить о получении трейда и выплате"""
    
    text = f"""
✅ <b>Трейд получен #{deal_id}</b>

💸 Выплата: {payout_amount:,.0f} ₽
📤 Деньги отправлены клиенту
"""
    
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await send_telegram_message(admin_id.strip(), text)


async def notify_buyback(deal_id: int, amount: float):
    """Уведомить о выкупе"""
    
    text = f"""
🔄 <b>Выкуп #{deal_id}</b>

💰 Получено: {amount:,.0f} ₽
📦 Отправить скины клиенту!
"""
    
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await send_telegram_message(admin_id.strip(), text)


async def notify_default(deal_id: int, items_count: int):
    """Уведомить о дефолте"""
    
    text = f"""
⚠️ <b>Дефолт #{deal_id}</b>

📦 Скинов: {items_count}
💎 Можно продавать!
"""
    
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await send_telegram_message(admin_id.strip(), text)
