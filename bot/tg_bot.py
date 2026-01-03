"""
КиберЛомбард Telegram Bot
Уведомления админам о новых сделках + базовые команды
"""

import os
import asyncio
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_CHAT_IDS = os.getenv("TELEGRAM_ADMIN_IDS", "").split(",")  # Через запятую
API_URL = os.getenv("API_URL", "http://localhost:8000")
SITE_URL = os.getenv("SITE_URL", "http://localhost:3000")

# Telegram API
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def send_message(chat_id: str, text: str, parse_mode: str = "HTML", reply_markup: dict = None):
    """Отправить сообщение в Telegram"""
    if not BOT_TOKEN:
        print(f"[TG BOT] No token, would send to {chat_id}: {text[:50]}...")
        return
    
    async with httpx.AsyncClient() as client:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            import json
            payload["reply_markup"] = json.dumps(reply_markup)
        
        try:
            response = await client.post(f"{TELEGRAM_API}/sendMessage", json=payload)
            return response.json()
        except Exception as e:
            print(f"[TG BOT] Error sending message: {e}")
            return None


async def notify_admins_new_deal(deal_data: dict):
    """Уведомить админов о новой сделке"""
    
    deal_id = deal_data.get("id", "?")
    loan_amount = deal_data.get("loan_amount", 0)
    items_count = len(deal_data.get("items_snapshot", []))
    kyc = deal_data.get("kyc_snapshot", {})
    user_name = kyc.get("full_name", "Неизвестно")
    phone = kyc.get("phone", "Не указан")
    
    text = f"""
🆕 <b>Новая сделка #{deal_id}</b>

👤 <b>Клиент:</b> {user_name}
📱 <b>Телефон:</b> {phone}
🎮 <b>Скинов:</b> {items_count}
💰 <b>Сумма:</b> {loan_amount:,.0f} ₽

⏳ Ожидает подтверждения трейда

🔗 <a href="{SITE_URL}/admin">Открыть админку</a>
"""
    
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Подтвердить", "callback_data": f"accept_{deal_id}"},
                {"text": "❌ Отклонить", "callback_data": f"reject_{deal_id}"}
            ],
            [{"text": "👁️ Подробнее", "url": f"{SITE_URL}/cabinet/deals/{deal_id}"}]
        ]
    }
    
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await send_message(admin_id.strip(), text, reply_markup=keyboard)


async def notify_admins_trade_received(deal_id: int, payout_amount: float):
    """Уведомить админов о получении трейда"""
    
    text = f"""
✅ <b>Трейд получен! Сделка #{deal_id}</b>

💸 Выплата: <b>{payout_amount:,.0f} ₽</b>
📤 Статус: Деньги отправлены клиенту

🔗 <a href="{SITE_URL}/cabinet/deals/{deal_id}">Открыть сделку</a>
"""
    
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await send_message(admin_id.strip(), text)


async def notify_admins_buyback(deal_id: int, amount: float):
    """Уведомить админов о выкупе"""
    
    text = f"""
🔄 <b>Выкуп! Сделка #{deal_id}</b>

💰 Получено: <b>{amount:,.0f} ₽</b>
📦 Нужно отправить скины обратно клиенту

🔗 <a href="{SITE_URL}/cabinet/deals/{deal_id}">Открыть сделку</a>
"""
    
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await send_message(admin_id.strip(), text)


async def notify_admins_default(deal_id: int, items_count: int):
    """Уведомить админов о дефолте"""
    
    text = f"""
⚠️ <b>Дефолт! Сделка #{deal_id}</b>

📦 Скинов: <b>{items_count}</b>
💎 Скины теперь наши - можно продавать

🔗 <a href="{SITE_URL}/cabinet/deals/{deal_id}">Открыть сделку</a>
"""
    
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await send_message(admin_id.strip(), text)


# ============= BOT COMMANDS =============

async def handle_start(chat_id: str, user_name: str):
    """Обработка /start"""
    
    text = f"""
👋 Привет, {user_name}!

Я бот <b>КиберЛомбарда</b> 🎮

Здесь ты можешь:
• Оценить свои CS2 скины
• Получить деньги под залог
• Выкупить скины обратно

🌐 <a href="{SITE_URL}">Перейти на сайт</a>
"""
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🎮 Оценить скины", "url": f"{SITE_URL}/cabinet/inventory"}],
            [{"text": "📋 Мои сделки", "url": f"{SITE_URL}/cabinet/deals"}],
            [{"text": "❓ Как это работает", "callback_data": "how_it_works"}]
        ]
    }
    
    # Если админ - добавить кнопку админки
    if chat_id in [a.strip() for a in ADMIN_CHAT_IDS]:
        keyboard["inline_keyboard"].append([
            {"text": "🔐 Админ-панель", "url": f"{SITE_URL}/admin"}
        ])
    
    await send_message(chat_id, text, reply_markup=keyboard)


async def handle_callback(chat_id: str, callback_data: str, message_id: int):
    """Обработка callback кнопок"""
    
    if callback_data == "how_it_works":
        text = """
<b>Как работает КиберЛомбард?</b>

1️⃣ Авторизуйся через Steam
2️⃣ Выбери скины для залога
3️⃣ Получи оценку (40% от рыночной цены)
4️⃣ Подпиши договор
5️⃣ Отправь скины трейдом
6️⃣ Получи деньги на карту/СБП

📅 Срок выкупа: 7-30 дней
💰 Переплата: 10-25%

Не выкупил вовремя = скины наши 🤷
"""
        await send_message(chat_id, text)
    
    elif callback_data.startswith("accept_"):
        deal_id = callback_data.replace("accept_", "")
        # Вызвать API
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(f"{API_URL}/api/deals/{deal_id}/accept")
                if res.status_code == 200:
                    await send_message(chat_id, f"✅ Сделка #{deal_id} подтверждена!")
                else:
                    await send_message(chat_id, f"❌ Ошибка: {res.text}")
            except Exception as e:
                await send_message(chat_id, f"❌ Ошибка: {e}")
    
    elif callback_data.startswith("reject_"):
        deal_id = callback_data.replace("reject_", "")
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(f"{API_URL}/api/admin/deals/{deal_id}/cancel")
                if res.status_code == 200:
                    await send_message(chat_id, f"❌ Сделка #{deal_id} отклонена")
                else:
                    await send_message(chat_id, f"❌ Ошибка: {res.text}")
            except Exception as e:
                await send_message(chat_id, f"❌ Ошибка: {e}")


async def handle_stats(chat_id: str):
    """Статистика для админа"""
    
    if chat_id not in [a.strip() for a in ADMIN_CHAT_IDS]:
        await send_message(chat_id, "⛔ Нет доступа")
        return
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(f"{API_URL}/api/admin/deals")
            data = res.json()
            deals = data.get("deals", [])
            
            stats = {"PENDING": 0, "ACTIVE": 0, "BUYBACK": 0, "DEFAULT": 0}
            total_loan = 0
            
            for d in deals:
                status = d.get("deal_status", "")
                if status in stats:
                    stats[status] += 1
                total_loan += d.get("loan_amount", 0)
            
            text = f"""
📊 <b>Статистика КиберЛомбарда</b>

📝 Всего сделок: <b>{len(deals)}</b>
⏳ Ожидают: <b>{stats['PENDING']}</b>
✅ Активные: <b>{stats['ACTIVE']}</b>
🔄 Выкуплены: <b>{stats['BUYBACK']}</b>
⚠️ Дефолт: <b>{stats['DEFAULT']}</b>

💰 Выдано всего: <b>{total_loan:,.0f} ₽</b>
"""
            await send_message(chat_id, text)
        except Exception as e:
            await send_message(chat_id, f"❌ Ошибка: {e}")


# ============= WEBHOOK / POLLING =============

async def process_update(update: dict):
    """Обработка входящего update от Telegram"""
    
    # Сообщение
    if "message" in update:
        msg = update["message"]
        chat_id = str(msg["chat"]["id"])
        text = msg.get("text", "")
        user_name = msg.get("from", {}).get("first_name", "друг")
        
        if text == "/start":
            await handle_start(chat_id, user_name)
        elif text == "/stats":
            await handle_stats(chat_id)
        elif text == "/help":
            await handle_start(chat_id, user_name)
    
    # Callback от inline кнопок
    elif "callback_query" in update:
        cb = update["callback_query"]
        chat_id = str(cb["message"]["chat"]["id"])
        message_id = cb["message"]["message_id"]
        callback_data = cb.get("data", "")
        
        await handle_callback(chat_id, callback_data, message_id)
        
        # Ответить на callback чтобы убрать "часики"
        if BOT_TOKEN:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{TELEGRAM_API}/answerCallbackQuery",
                    json={"callback_query_id": cb["id"]}
                )


async def polling():
    """Long polling для получения updates"""
    
    if not BOT_TOKEN:
        print("[TG BOT] No TELEGRAM_BOT_TOKEN, bot disabled")
        return
    
    print(f"[TG BOT] Starting polling...")
    offset = 0
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            try:
                response = await client.get(
                    f"{TELEGRAM_API}/getUpdates",
                    params={"offset": offset, "timeout": 30}
                )
                data = response.json()
                
                if data.get("ok"):
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        await process_update(update)
                
            except Exception as e:
                print(f"[TG BOT] Polling error: {e}")
                await asyncio.sleep(5)


if __name__ == "__main__":
    print("[TG BOT] КиберЛомбард Bot starting...")
    asyncio.run(polling())
