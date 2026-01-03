from fastapi import FastAPI, Depends, HTTPException, status, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import httpx
import asyncio
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import models
import schemas
from database import engine, get_db
from services.steam_service import SteamService
from services.pricing_service import PricingService
from services.sms_service import SMSService
from services.contract_service import ContractService
from services.payment_service import PaymentService
from services.steam_auth_service import SteamAuthService
from services.passport_ocr_service import PassportOCRService
from config import get_settings
from logger import logger
from validators import (
    validate_steam_id, validate_phone, validate_asset_id,
    validate_option_days, validate_amount, validate_sms_code
)

# Создание таблиц
models.Base.metadata.create_all(bind=engine)

# Создать папку contracts если нет
os.makedirs("contracts", exist_ok=True)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="КиберЛомбард CS2 API",
    description="API для выкупа цифровых прав на CS2 скины с опционом обратного выкупа",
    version="1.0.0"
)

# Раздача статических файлов (договоры PDF)
app.mount("/contracts", StaticFiles(directory="contracts"), name="contracts")

# Добавить rate limiter в app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

settings = get_settings()

logger.info("КиберЛомбард API запущен")

# CORS
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

# Добавить production домены из env
if settings.production_domain:
    allowed_origins.append(f"https://{settings.production_domain}")
    allowed_origins.append(f"https://www.{settings.production_domain}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= AUTH ENDPOINTS =============

@app.get("/api/auth/steam/login")
async def steam_login(return_url: str):
    """Получить URL для Steam OpenID авторизации"""
    
    login_url = SteamAuthService.get_login_url(return_url)
    
    return {
        "login_url": login_url
    }

@app.get("/api/auth/steam/callback")
@limiter.limit("10/minute")
async def steam_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """Callback после Steam авторизации"""
    
    logger.info(f"[AUTH] Steam callback получен")
    
    # Получить все query параметры
    params = dict(request.query_params)
    
    # Верифицировать OpenID ответ
    steam_id = await SteamAuthService.verify_openid_response(params)
    
    if not steam_id:
        logger.warning(f"[AUTH] Steam авторизация не прошла")
        raise HTTPException(status_code=400, detail="Steam авторизация не прошла")
    
    if not validate_steam_id(steam_id):
        logger.error(f"[AUTH] Неверный Steam ID: {steam_id}")
        raise HTTPException(status_code=400, detail="Неверный Steam ID")
    
    # Получить инфо из Steam API
    user_info = await SteamService.get_user_info(steam_id)
    
    if not user_info:
        raise HTTPException(status_code=404, detail="Steam user not found")
    
    # Найти или создать пользователя
    user = db.query(models.User).filter(models.User.steam_id == steam_id).first()
    
    if not user:
        user = models.User(
            steam_id=steam_id,
            steam_username=user_info["username"],
            steam_avatar=user_info["avatar"]
        )
        db.add(user)
    else:
        user.steam_username = user_info["username"]
        user.steam_avatar = user_info["avatar"]
        user.last_login = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    # Логирование
    audit_log = models.AuditLog(
        user_id=user.id,
        action="steam_login",
        details={
            "steam_id": steam_id,
            "username": user_info["username"]
        }
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "steam_id": user.steam_id,
            "steam_username": user.steam_username,
            "steam_avatar": user.steam_avatar,
            "phone_verified": user.phone_verified,
            "passport_verified": user.passport_verified
        }
    }

@app.post("/api/auth/steam/verify", response_model=schemas.User)
async def verify_steam_user(
    steam_id: str,
    db: Session = Depends(get_db)
):
    """Верификация пользователя через Steam OpenID (альтернативный метод)"""
    
    # Получить инфо из Steam API
    user_info = await SteamService.get_user_info(steam_id)
    
    if not user_info:
        raise HTTPException(status_code=404, detail="Steam user not found")
    
    # Найти или создать пользователя
    user = db.query(models.User).filter(models.User.steam_id == steam_id).first()
    
    if not user:
        user = models.User(
            steam_id=steam_id,
            steam_username=user_info["username"],
            steam_avatar=user_info["avatar"]
        )
        db.add(user)
    else:
        user.steam_username = user_info["username"]
        user.steam_avatar = user_info["avatar"]
        user.last_login = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return user

# ============= KYC ENDPOINTS =============

@app.post("/api/kyc/phone/send-code")
@limiter.limit("5/minute")
async def send_phone_verification(
    request: Request,
    phone: str,
    db: Session = Depends(get_db)
):
    """Отправить SMS-код для верификации телефона"""
    
    logger.info(f"[KYC] Запрос SMS кода для {phone}")
    
    # Проверка формата телефона (РФ)
    if not validate_phone(phone):
        logger.warning(f"[KYC] Неверный формат телефона: {phone}")
        raise HTTPException(status_code=400, detail="Неверный формат телефона")
    
    code = SMSService.create_verification(db, phone, "phone_verify")
    
    return {
        "success": True,
        "message": "SMS-код отправлен",
        "dev_code": code  # Только для разработки!
    }

@app.post("/api/kyc/phone/verify")
async def verify_phone(
    phone: str,
    code: str,
    steam_id: str,
    db: Session = Depends(get_db)
):
    """Подтвердить телефон по SMS-коду"""
    
    if not SMSService.verify_code(db, phone, code, "phone_verify"):
        raise HTTPException(status_code=400, detail="Неверный или истекший код")
    
    user = db.query(models.User).filter(models.User.steam_id == steam_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user.phone = phone
    user.phone_verified = True
    db.commit()
    
    return {"success": True, "message": "Телефон подтвержден"}

@app.post("/api/kyc/passport")
async def submit_passport(
    steam_id: str,
    kyc_data: schemas.UserKYC,
    db: Session = Depends(get_db)
):
    """Отправить паспортные данные"""
    
    user = db.query(models.User).filter(models.User.steam_id == steam_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user.passport_series = kyc_data.passport_series
    user.passport_number = kyc_data.passport_number
    user.passport_issued_by = kyc_data.passport_issued_by
    user.passport_department_code = kyc_data.passport_department_code
    user.passport_verified = True  # В проде - ручная модерация
    
    db.commit()
    
    return {"success": True, "message": "Паспортные данные сохранены"}

@app.post("/api/kyc/passport/scan")
async def scan_passport(request: Request):
    """
    Распознать паспорт из фото (OCR)
    
    Body: { "image": "base64_encoded_image" }
    
    Returns: распознанные данные паспорта
    """
    try:
        body = await request.json()
        image_base64 = body.get("image", "")
        
        if not image_base64:
            raise HTTPException(status_code=400, detail="Изображение не предоставлено")
        
        # Распознаём паспорт (async для Yandex Vision)
        passport_data = await PassportOCRService.extract_from_base64(image_base64)
        result = PassportOCRService.to_dict(passport_data)
        
        logger.info(f"[OCR] Распознан паспорт: {result.get('full_name', 'N/A')}, confidence: {result.get('confidence', 0)}")
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"[OCR] Ошибка: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка распознавания: {str(e)}")

# ============= INVENTORY ENDPOINTS =============

@app.post("/api/user/trade-url")
async def save_trade_url(
    steam_id: str,
    trade_url: str,
    db: Session = Depends(get_db)
):
    """Сохранить trade URL пользователя"""
    
    # Парсим trade URL
    parsed = SteamAuthService.parse_trade_url(trade_url)
    
    if not parsed:
        raise HTTPException(status_code=400, detail="Неверный формат trade URL")
    
    # Проверяем что steam_id совпадает
    if parsed["steam_id64"] != steam_id:
        raise HTTPException(
            status_code=400, 
            detail=f"Steam ID из trade URL ({parsed['steam_id64']}) не совпадает с вашим ({steam_id})"
        )
    
    # Находим или создаем пользователя
    user = db.query(models.User).filter(models.User.steam_id == steam_id).first()
    
    if not user:
        user = models.User(
            steam_id=steam_id,
            trade_url=trade_url,
            trade_token=parsed["trade_token"]
        )
        db.add(user)
    else:
        user.trade_url = trade_url
        user.trade_token = parsed["trade_token"]
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "steam_id": steam_id,
        "trade_token": parsed["trade_token"]
    }

@app.get("/api/inventory/{steam_id}", response_model=schemas.InventoryResponse)
@limiter.limit("10/minute")
async def get_inventory(
    request: Request,
    steam_id: str,
    db: Session = Depends(get_db)
):
    """Получить CS2 инвентарь с live ценами (Lis-Skins + market.csgo + Steam)"""
    
    logger.info(f"[INVENTORY] Запрос инвентаря для {steam_id}")
    
    if not validate_steam_id(steam_id):
        logger.error(f"[INVENTORY] Неверный Steam ID: {steam_id}")
        raise HTTPException(status_code=400, detail="Неверный Steam ID")
    
    # Получить инвентарь
    items = await SteamService.get_inventory(steam_id)
    
    if not items:
        return schemas.InventoryResponse(
            steam_id=steam_id,
            items=[],
            total_value=0.0,
            last_updated=datetime.utcnow()
        )
    
    # Получить цены из market.csgo
    prices = await SteamService.get_market_prices(items)
    
    # Добавить цены к предметам
    items_with_prices = []
    total_value = 0.0
    
    for item in items:
        market_name = item["market_hash_name"]
        price_data = prices.get(market_name, {})
        
        # Извлекаем цены (новая структура)
        market_csgo_price = price_data.get("market_csgo_price", 0.0)
        lis_estimate = price_data.get("lis_skins_estimate", 0.0)
        instant_price = price_data.get("instant_price", 0.0)
        is_acceptable = price_data.get("is_acceptable", False)
        
        # Если нет цены, используем fallback по редкости
        if instant_price == 0:
            instant_price = SteamService._estimate_price_by_rarity(
                item.get("rarity"),
                item.get("type", "")
            )
            is_acceptable = instant_price >= 40  # Минимум 40₽
        
        # Рассчитываем залог (50% от цены)
        loan_amount = instant_price * 0.50
        
        items_with_prices.append({
            **item,
            "market_price": instant_price,  # Для совместимости
            "instant_price": instant_price,
            "market_csgo_price": market_csgo_price,
            "lis_skins_estimate": lis_estimate,
            "loan_amount": loan_amount,  # Сумма залога
            "is_acceptable": is_acceptable,
            "is_estimated": not is_acceptable
        })
        
        if instant_price > 0:
            total_value += instant_price
    
    # Сортировка по цене (дорогие первые)
    items_with_prices.sort(key=lambda x: x["instant_price"], reverse=True)
    
    return schemas.InventoryResponse(
        steam_id=steam_id,
        items=items_with_prices,
        total_value=total_value,
        last_updated=datetime.utcnow()
    )

@app.post("/api/inventory/authenticated/{steam_id}")
async def get_inventory_authenticated(
    steam_id: str,
    cookies: dict,
    db: Session = Depends(get_db)
):
    """
    Получить инвентарь с использованием Steam cookies
    
    Для продвинутых пользователей: позволяет загрузить даже приватный инвентарь
    если предоставлены правильные cookies из авторизованной сессии Steam
    
    Body:
    {
        "sessionid": "xxx",
        "steamLoginSecure": "yyy"
    }
    """
    from services.steam_authenticated_inventory import SteamAuthenticatedInventory
    
    session_id = cookies.get("sessionid")
    steam_login_secure = cookies.get("steamLoginSecure")
    
    # Загрузить инвентарь с cookies
    items = await SteamAuthenticatedInventory.get_inventory_with_cookies(
        steam_id=steam_id,
        session_id=session_id,
        steam_login_secure=steam_login_secure
    )
    
    if not items:
        # Fallback на публичный метод
        items = await SteamAuthenticatedInventory.get_inventory_public(steam_id)
    
    # Получить цены
    prices = await SteamService.get_market_prices(items)
    
    # Добавить цены к предметам
    items_with_prices = []
    total_value = 0.0
    
    for item in items:
        market_name = item["market_hash_name"]
        price = prices.get(market_name, 0.0)
        
        items_with_prices.append({
            **item,
            "market_price": price
        })
        total_value += price
    
    return {
        "steam_id": steam_id,
        "items": items_with_prices,
        "total_value": total_value,
        "last_updated": datetime.utcnow(),
        "method": "authenticated" if session_id else "public"
    }

# ============= QUOTE ENDPOINTS =============

@app.post("/api/quote", response_model=schemas.QuoteResponse)
@limiter.limit("20/minute")
async def calculate_quote(
    request: Request,
    quote_request: schemas.QuoteRequest,
    db: Session = Depends(get_db)
):
    """Рассчитать условия сделки"""
    
    logger.info(f"[QUOTE] Запрос: steam_id={quote_request.steam_id}, asset_ids={quote_request.asset_ids}")
    
    if not validate_steam_id(quote_request.steam_id):
        logger.error(f"[QUOTE] Неверный Steam ID: {quote_request.steam_id}")
        raise HTTPException(status_code=400, detail="Неверный Steam ID")
    
    if not validate_option_days(quote_request.option_days):
        logger.error(f"[QUOTE] Неверный срок опциона: {quote_request.option_days}")
        raise HTTPException(status_code=400, detail="Срок опциона должен быть 7-30 дней")
    
    print(f"[QUOTE] Запрос: steam_id={quote_request.steam_id}, asset_ids={quote_request.asset_ids}")
    
    # Получить инвентарь
    all_items = await SteamService.get_inventory(quote_request.steam_id)
    print(f"[QUOTE] Загружено {len(all_items)} предметов из инвентаря")
    
    # Фильтровать выбранные предметы
    selected_items = [
        item for item in all_items 
        if item["assetid"] in quote_request.asset_ids
    ]
    
    print(f"[QUOTE] Найдено {len(selected_items)} выбранных предметов")
    
    if not selected_items:
        print(f"[QUOTE] WARNING: Предметы не найдены по asset_ids={quote_request.asset_ids}")
        print(f"[QUOTE] Доступные assetid: {[item['assetid'] for item in all_items[:5]]}")
        # Fallback: используем первые 5 предметов для демонстрации
        selected_items = all_items[:5]
        print(f"[QUOTE] Используем fallback: первые {len(selected_items)} предметов")
    
    # Получить цены Steam Market
    prices = await SteamService.get_market_prices(selected_items)
    
    items_with_prices = []
    for item in selected_items:
        market_name = item["market_hash_name"]
        price_data = prices.get(market_name, 0.0)
        
        # Если price_data это dict, извлекаем цену
        if isinstance(price_data, dict):
            price = price_data.get("instant_price", 0.0)
        else:
            price = price_data if isinstance(price_data, (int, float)) else 0.0
        
        # Минимум 10₽ для работы с предметом
        if price < 10.0:
            # Fallback: оценка по редкости
            price = SteamService._estimate_price_by_rarity(
                item.get("rarity"),
                item.get("type", "")
            )
            if price < 10.0:
                price = 0.0
        
        items_with_prices.append({
            **item,
            "instant_price": price,
            "market_price": price,  # Для обратной совместимости
            "is_estimated": False
        })
    
    # Рассчитать условия (залог = 30% от Steam Market)
    quote = PricingService.calculate_quote(
        items_with_prices,
        quote_request.option_days
    )
    
    # Логирование для отладки
    print(f"[QUOTE] Предметов: {len(items_with_prices)}")
    print(f"[QUOTE] Рыночная стоимость: {quote['market_total']} ₽")
    print(f"[QUOTE] Залог: {quote['loan_amount']} ₽")
    print(f"[QUOTE] Выкуп: {quote['buyback_price']} ₽")
    
    return schemas.QuoteResponse(**quote)

# ============= DEAL ENDPOINTS =============

@app.post("/api/deals", response_model=schemas.DealResponse)
@limiter.limit("5/minute")
async def create_deal(
    request: Request,
    deal_create: schemas.DealCreate,
    db: Session = Depends(get_db)
):
    """Создать сделку"""
    
    logger.info(f"[DEAL] Создание сделки для {deal_create.quote_request.steam_id}")
    
    if not validate_steam_id(deal_create.quote_request.steam_id):
        logger.error(f"[DEAL] Неверный Steam ID")
        raise HTTPException(status_code=400, detail="Неверный Steam ID")
    
    if not validate_sms_code(deal_create.sms_code):
        logger.error(f"[DEAL] Неверный формат SMS кода")
        raise HTTPException(status_code=400, detail="Неверный формат SMS кода")
    
    # Получить пользователя
    user = db.query(models.User).filter(
        models.User.steam_id == deal_create.quote_request.steam_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверить верификацию телефона (пропускаем в DEV режиме)
    skip_verification = getattr(deal_create, 'skip_verification', False)
    if not skip_verification and not user.phone_verified:
        raise HTTPException(status_code=400, detail="Необходимо подтвердить телефон")
    
    # Пересчитать quote
    all_items = await SteamService.get_inventory(deal_create.quote_request.steam_id)
    selected_items = [
        item for item in all_items 
        if item["assetid"] in deal_create.quote_request.asset_ids
    ]
    
    prices = await SteamService.get_market_prices(selected_items)
    items_with_prices = []
    for item in selected_items:
        market_name = item["market_hash_name"]
        price_data = prices.get(market_name, {})
        
        # Извлекаем цену из объекта
        if isinstance(price_data, dict):
            instant_price = price_data.get("instant_price", 0.0)
        else:
            instant_price = price_data if isinstance(price_data, (int, float)) else 0.0
        
        # Fallback по редкости если цена 0
        if instant_price == 0:
            instant_price = SteamService._estimate_price_by_rarity(
                item.get("rarity"),
                item.get("type", "")
            )
        
        items_with_prices.append({
            **item,
            "market_price": instant_price,  # Число, не объект
            "instant_price": instant_price
        })
    
    quote = PricingService.calculate_quote(
        items_with_prices,
        deal_create.quote_request.option_days
    )
    
    # Проверить KYC для больших сумм (пропускаем в DEV режиме)
    if not skip_verification and PricingService.check_kyc_required(quote["loan_amount"]):
        if not user.passport_verified:
            raise HTTPException(
                status_code=400,
                detail=f"Для сумм >15000₽ требуется паспорт"
            )
    
    # Проверить SMS-код (пропускаем в DEV режиме)
    if not skip_verification:
        if not SMSService.verify_code(db, user.phone, deal_create.sms_code, "deal_sign"):
            raise HTTPException(status_code=400, detail="Неверный SMS-код")
    
    # Подготовить KYC snapshot
    kyc_snapshot = None
    if deal_create.kyc_data:
        kyc_snapshot = {
            "full_name": deal_create.kyc_data.full_name,
            "passport_series": deal_create.kyc_data.passport_series,
            "passport_number": deal_create.kyc_data.passport_number,
            "birth_date": deal_create.kyc_data.birth_date,
            "department_code": deal_create.kyc_data.department_code,
            "registration_address": deal_create.kyc_data.registration_address,
            "phone": deal_create.kyc_data.phone or user.phone,
            "steam_id": user.steam_id,
            "steam_username": user.steam_username
        }
    
    # Создать сделку
    deal = models.Deal(
        user_id=user.id,
        market_total=quote["market_total"],
        loan_amount=quote["loan_amount"],
        buyback_price=quote["buyback_price"],
        option_expiry=quote["option_expiry"],
        items_snapshot=items_with_prices,
        kyc_snapshot=kyc_snapshot,
        deal_status=models.DealStatus.PENDING,
        signature_sms_code=SMSService.hash_code(deal_create.sms_code),
        signature_timestamp=datetime.utcnow()
    )
    
    db.add(deal)
    db.commit()
    db.refresh(deal)
    
    # Генерировать PDF договора
    contract_path = f"contracts/deal_{deal.id}.pdf"
    ContractService.generate_contract_pdf(
        deal={
            "id": deal.id,
            "market_total": deal.market_total,
            "loan_amount": deal.loan_amount,
            "buyback_price": deal.buyback_price,
            "option_expiry": deal.option_expiry,
            "option_days": deal_create.quote_request.option_days,
            "signature_timestamp": deal.signature_timestamp,
            "signature_sms_code": deal.signature_sms_code,
            "items": items_with_prices,
            "created_at": datetime.utcnow(),
            "term_config": quote.get("term_config", {"interest": 0.15, "premium": 0.07})
        },
        user={
            "steam_id": user.steam_id,
            "phone": user.phone or "+7XXXXXXXXXX",
            "passport_series": user.passport_series or "XXXX",
            "passport_number": user.passport_number or "XXXXXX",
            "full_name": "Клиент"
        },
        output_path=contract_path
    )
    
    # Сохраняем путь к договору
    deal.contract_pdf_url = contract_path
    db.commit()
    
    # Создать Steam Trade Offer через бота
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            bot_response = await client.post(
                "http://localhost:3001/api/trade/create",
                json={
                    "deal_id": deal.id,
                    "partner_steam_id": user.steam_id,
                    "items": [
                        {"assetid": item["assetid"]} 
                        for item in items_with_prices
                    ]
                }
            )
            
            if bot_response.status_code == 200:
                trade_data = bot_response.json()
                deal.initial_trade_id = trade_data.get("trade_offer_id")
                deal.initial_trade_url = trade_data.get("trade_url")
                
                # Создать запись трейда
                trade = models.SteamTrade(
                    deal_id=deal.id,
                    trade_offer_id=trade_data["trade_offer_id"],
                    trade_offer_url=trade_data["trade_url"],
                    is_incoming=True,
                    status=models.TradeStatus.SENT,
                    items_json=items_with_prices
                )
                db.add(trade)
                db.commit()
                
                print(f"[API] Трейд создан: {trade_data['trade_url']}")
    except Exception as e:
        print(f"[API] Ошибка создания трейда: {e}")
        # Продолжаем без трейда - можно создать вручную
    
    db.refresh(deal)
    return deal

@app.get("/api/deals", response_model=List[schemas.DealResponse])
async def get_user_deals(
    steam_id: str,
    db: Session = Depends(get_db)
):
    """Получить все сделки пользователя"""
    
    user = db.query(models.User).filter(models.User.steam_id == steam_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    deals = db.query(models.Deal).filter(models.Deal.user_id == user.id).all()
    
    return deals

@app.get("/api/deals/{deal_id}", response_model=schemas.DealDetail)
async def get_deal(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """Получить детали сделки"""
    
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    
    # Получаем пользователя
    user = db.query(models.User).filter(models.User.id == deal.user_id).first()
    
    # Вычисляемые поля
    now = datetime.utcnow()
    is_expired = now > deal.option_expiry
    can_buyback = (
        deal.deal_status == models.DealStatus.ACTIVE and 
        not is_expired
    )
    
    days_left = None
    if not is_expired:
        days_left = (deal.option_expiry - now).days
    
    deal_dict = {
        **deal.__dict__,
        "user": user,
        "is_expired": is_expired,
        "can_buyback": can_buyback,
        "days_left": days_left
    }
    
    return deal_dict

@app.post("/api/deals/{deal_id}/accept")
async def accept_deal_trade(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """Подтвердить получение трейда и выплатить деньги"""
    
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    
    if deal.deal_status != models.DealStatus.PENDING:
        raise HTTPException(status_code=400, detail="Сделка уже обработана")
    
    # Проверить статус трейда через Steam Bot API
    if deal.initial_trade_id:
        try:
            bot_response = await httpx.AsyncClient().get(
                f"http://localhost:3001/api/trade/status/{deal.initial_trade_id}"
            )
            if bot_response.status_code == 200:
                trade_data = bot_response.json()
                if trade_data.get("status") != "ACCEPTED":
                    raise HTTPException(status_code=400, detail="Трейд еще не принят")
        except Exception as e:
            print(f"[API] Ошибка проверки трейда: {e}")
    
    # Обновить статус
    deal.deal_status = models.DealStatus.ACTIVE
    
    # Получить телефон из kyc_snapshot или user
    phone = None
    if deal.kyc_snapshot and isinstance(deal.kyc_snapshot, dict):
        phone = deal.kyc_snapshot.get("phone")
    if not phone:
        phone = user.phone
    
    # Инициировать выплату через ЮKassa/СБП
    if phone:
        payout_id = await PaymentService.create_payout(
            phone=phone,
            amount=deal.loan_amount,
            description=f"Выплата по сделке #{deal.id}",
            deal_id=deal.id
        )
        
        if payout_id:
            deal.payout_transaction_id = payout_id
            print(f"[DEAL] Выплата инициирована: {payout_id} на {phone}")
    else:
        print(f"[DEAL] Внимание: телефон не указан, выплата не инициирована")
    
    db.commit()
    
    # Логирование
    audit_log = models.AuditLog(
        user_id=user.id,
        action="deal_activated",
        details={
            "deal_id": deal.id,
            "payout_id": payout_id,
            "amount": deal.loan_amount
        }
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "success": True,
        "message": "Сделка активирована, деньги отправлены",
        "deal_status": deal.deal_status,
        "payout_id": payout_id
    }

@app.post("/api/deals/{deal_id}/buyback/init")
async def init_buyback(
    deal_id: int,
    return_url: str,
    db: Session = Depends(get_db)
):
    """Инициировать выкуп - создать платеж"""
    
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    
    if deal.deal_status != models.DealStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Сделка не активна")
    
    now = datetime.utcnow()
    if now > deal.option_expiry:
        deal.deal_status = models.DealStatus.DEFAULT
        db.commit()
        raise HTTPException(status_code=400, detail="Срок опциона истек")
    
    # Создать платеж
    payment_data = await PaymentService.create_payment(
        amount=deal.buyback_price,
        description=f"Выкуп скинов по сделке #{deal.id}",
        return_url=return_url,
        deal_id=deal.id
    )
    
    if not payment_data:
        raise HTTPException(status_code=500, detail="Ошибка создания платежа")
    
    return {
        "success": True,
        "payment_id": payment_data["payment_id"],
        "confirmation_url": payment_data["confirmation_url"],
        "amount": deal.buyback_price
    }

@app.post("/api/deals/{deal_id}/buyback/complete")
async def complete_buyback(
    deal_id: int,
    payment_id: str,
    db: Session = Depends(get_db)
):
    """Завершить выкуп после оплаты"""
    
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    
    if deal.deal_status != models.DealStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Сделка не активна")
    
    # Проверить оплату
    payment_status = await PaymentService.check_payment_status(payment_id)
    if payment_status != "succeeded":
        raise HTTPException(status_code=400, detail="Оплата не подтверждена")
    
    # Обновить сделку
    now = datetime.utcnow()
    deal.deal_status = models.DealStatus.BUYBACK
    deal.buyback_at = now
    deal.buyback_payment_id = payment_id
    db.commit()
    
    # Создать обратный трейд через Steam Bot
    user = deal.user
    try:
        bot_response = await httpx.AsyncClient().post(
            "http://localhost:3001/api/trade/reverse",
            json={
                "deal_id": deal.id,
                "partner_steam_id": user.steam_id,
                "items": deal.items_snapshot
            },
            timeout=30.0
        )
        
        if bot_response.status_code == 200:
            trade_data = bot_response.json()
            deal.buyback_trade_id = trade_data.get("trade_offer_id")
            
            # Создать запись трейда
            trade = models.SteamTrade(
                deal_id=deal.id,
                trade_offer_id=trade_data["trade_offer_id"],
                trade_offer_url=trade_data["trade_url"],
                is_incoming=False,
                status=models.TradeStatus.SENT,
                items_json=deal.items_snapshot
            )
            db.add(trade)
            db.commit()
            
            return {
                "success": True,
                "message": "Выкуп оформлен, трейд отправлен",
                "trade_url": trade_data["trade_url"]
            }
    except Exception as e:
        print(f"[API] Ошибка создания обратного трейда: {e}")
    
    return {
        "success": True,
        "message": "Выкуп оформлен, трейд будет отправлен вручную",
        "trade_url": None
    }

# ============= ADMIN ENDPOINTS =============

@app.post("/api/admin/deals/{deal_id}/default")
async def mark_deal_default(
    deal_id: int,
    db: Session = Depends(get_db)
):
    """Перевести просроченную сделку в дефолт (cron job)"""
    
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Сделка не найдена")
    
    now = datetime.utcnow()
    if now > deal.option_expiry and deal.deal_status == models.DealStatus.ACTIVE:
        deal.deal_status = models.DealStatus.DEFAULT
        db.commit()
        
        return {"success": True, "message": "Сделка переведена в дефолт"}
    
    return {"success": False, "message": "Условия для дефолта не выполнены"}

# ============= STEAM BOT WEBHOOK =============

@app.get("/api/trades/verify/{trade_offer_id}")
async def verify_trade(
    trade_offer_id: str,
    db: Session = Depends(get_db)
):
    """
    Проверить, ожидаем ли мы этот трейд.
    Вызывается Steam ботом при получении входящего трейда.
    """
    # Ищем сделку в статусе PENDING
    # В реальности нужно проверять предметы в трейде
    pending_deals = db.query(models.Deal).filter(
        models.Deal.deal_status == models.DealStatus.PENDING
    ).all()
    
    if pending_deals:
        # Для MVP принимаем любой трейд если есть ожидающие сделки
        # В проде нужно сверять предметы
        deal = pending_deals[0]
        return {
            "valid": True,
            "deal_id": deal.id,
            "expected_items": len(deal.items_snapshot)
        }
    
    return {"valid": False, "reason": "Нет ожидающих сделок"}

@app.post("/api/trades/{trade_offer_id}/status")
async def trade_status_webhook(
    trade_offer_id: str,
    status: str = Body(...),
    deal_id: int = Body(None),
    db: Session = Depends(get_db)
):
    """
    Webhook от Steam бота при изменении статуса трейда.
    Автоматически активирует сделку и выплачивает деньги.
    """
    print(f"[WEBHOOK] Трейд #{trade_offer_id} статус: {status}, deal_id: {deal_id}")
    
    if status != "ACCEPTED":
        return {"success": True, "message": f"Статус {status} не требует действий"}
    
    # Найти сделку
    deal = None
    if deal_id:
        deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    
    if not deal:
        # Попробовать найти по trade_id
        trade = db.query(models.SteamTrade).filter(
            models.SteamTrade.trade_offer_id == trade_offer_id
        ).first()
        if trade:
            deal = db.query(models.Deal).filter(models.Deal.id == trade.deal_id).first()
    
    if not deal:
        print(f"[WEBHOOK] Сделка не найдена для трейда #{trade_offer_id}")
        return {"success": False, "message": "Сделка не найдена"}
    
    if deal.deal_status != models.DealStatus.PENDING:
        print(f"[WEBHOOK] Сделка #{deal.id} уже обработана (статус: {deal.deal_status})")
        return {"success": True, "message": "Сделка уже обработана"}
    
    # Активировать сделку
    deal.deal_status = models.DealStatus.ACTIVE
    deal.initial_trade_id = trade_offer_id
    
    # Получить телефон для выплаты
    phone = None
    if deal.kyc_snapshot and isinstance(deal.kyc_snapshot, dict):
        phone = deal.kyc_snapshot.get("phone")
    if not phone and deal.user:
        phone = deal.user.phone
    
    # Выплатить деньги
    payout_id = None
    if phone:
        payout_id = await PaymentService.create_payout(
            phone=phone,
            amount=deal.loan_amount,
            description=f"Выплата по сделке #{deal.id}",
            deal_id=deal.id
        )
        if payout_id:
            deal.payout_transaction_id = payout_id
            print(f"[WEBHOOK] ✅ Выплата {deal.loan_amount}₽ инициирована: {payout_id}")
    else:
        print(f"[WEBHOOK] ⚠️ Телефон не указан, выплата не инициирована")
    
    db.commit()
    
    print(f"[WEBHOOK] ✅ Сделка #{deal.id} активирована автоматически!")
    
    return {
        "success": True,
        "message": "Сделка активирована, деньги отправлены",
        "deal_id": deal.id,
        "payout_id": payout_id
    }

# ============= HEALTH CHECK =============

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Расширенная проверка здоровья сервиса"""
    health_status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Проверка БД
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Проверка Steam API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://api.steampowered.com/ISteamWebAPIUtil/GetServerInfo/v1/")
            health_status["checks"]["steam_api"] = "ok" if response.status_code == 200 else "error"
    except Exception:
        health_status["checks"]["steam_api"] = "error"
        health_status["status"] = "degraded"
    
    # Проверка market.csgo API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://market.csgo.com/api/v2/prices/RUB.json")
            health_status["checks"]["market_csgo"] = "ok" if response.status_code == 200 else "error"
    except Exception:
        health_status["checks"]["market_csgo"] = "error"
    
    return health_status


@app.get("/health/simple")
async def simple_health_check():
    """Простая проверка (для load balancer)"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============= STATISTICS ENDPOINTS =============

@app.get("/api/stats/public")
async def get_public_stats(db: Session = Depends(get_db)):
    """Получить публичную статистику сервиса"""
    
    total_deals = db.query(models.Deal).count()
    active_deals = db.query(models.Deal).filter(
        models.Deal.deal_status == models.DealStatus.ACTIVE
    ).count()
    
    total_volume = db.query(func.sum(models.Deal.loan_amount)).scalar() or 0
    
    avg_deal_amount = db.query(func.avg(models.Deal.loan_amount)).scalar() or 0
    
    buyback_count = db.query(models.Deal).filter(
        models.Deal.deal_status == models.DealStatus.BUYBACK
    ).count()
    
    buyback_rate = (buyback_count / total_deals * 100) if total_deals > 0 else 0
    
    return {
        "total_deals": total_deals,
        "active_deals": active_deals,
        "total_volume": round(total_volume, 2),
        "avg_deal_amount": round(avg_deal_amount, 2),
        "buyback_rate": round(buyback_rate, 2)
    }

@app.get("/api/stats/user/{steam_id}")
async def get_user_stats(
    steam_id: str,
    db: Session = Depends(get_db)
):
    """Получить статистику пользователя"""
    
    user = db.query(models.User).filter(models.User.steam_id == steam_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    total_deals = db.query(models.Deal).filter(models.Deal.user_id == user.id).count()
    
    active_deals = db.query(models.Deal).filter(
        models.Deal.user_id == user.id,
        models.Deal.deal_status == models.DealStatus.ACTIVE
    ).count()
    
    total_received = db.query(func.sum(models.Deal.loan_amount)).filter(
        models.Deal.user_id == user.id
    ).scalar() or 0
    
    total_paid_back = db.query(func.sum(models.Deal.buyback_price)).filter(
        models.Deal.user_id == user.id,
        models.Deal.deal_status == models.DealStatus.BUYBACK
    ).scalar() or 0
    
    buyback_count = db.query(models.Deal).filter(
        models.Deal.user_id == user.id,
        models.Deal.deal_status == models.DealStatus.BUYBACK
    ).count()
    
    default_count = db.query(models.Deal).filter(
        models.Deal.user_id == user.id,
        models.Deal.deal_status == models.DealStatus.DEFAULT
    ).count()
    
    return {
        "total_deals": total_deals,
        "active_deals": active_deals,
        "buyback_count": buyback_count,
        "default_count": default_count,
        "total_received": round(total_received, 2),
        "total_paid_back": round(total_paid_back, 2),
        "member_since": user.created_at.isoformat()
    }

# ============= MARKET PRICES ENDPOINTS =============

@app.get("/api/prices/item/{market_hash_name}")
async def get_item_price(market_hash_name: str):
    """Получить цену конкретного предмета"""
    
    prices = await SteamService.get_market_prices([{"market_hash_name": market_hash_name}])
    
    if market_hash_name not in prices:
        raise HTTPException(status_code=404, detail="Цена не найдена")
    
    return {
        "market_hash_name": market_hash_name,
        "price": prices[market_hash_name],
        "currency": "RUB",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/prices/bulk")
async def get_bulk_prices(items: List[str]):
    """Получить цены для списка предметов"""
    
    items_list = [{"market_hash_name": name} for name in items]
    prices = await SteamService.get_market_prices(items_list)
    
    return {
        "prices": prices,
        "currency": "RUB",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============= CALCULATOR ENDPOINT =============

@app.post("/api/calculator")
async def calculate_deal_terms(
    market_price: float,
    option_days: int = 14
):
    """Калькулятор условий сделки"""
    
    if market_price <= 0:
        raise HTTPException(status_code=400, detail="Цена должна быть больше 0")
    
    if option_days < 7 or option_days > 30:
        raise HTTPException(status_code=400, detail="Срок опциона: 7-30 дней")
    
    items_with_prices = [{"market_price": market_price}]
    quote = PricingService.calculate_quote(items_with_prices, option_days)
    
    profit = PricingService.calculate_profit(quote)
    
    return {
        **quote,
        "profit_analysis": profit
    }

# ============= NOTIFICATIONS ENDPOINT =============

@app.post("/api/notifications/expiring-deals")
async def notify_expiring_deals(db: Session = Depends(get_db)):
    """Уведомить о истекающих сделках (cron job)"""
    
    # Сделки истекающие в течение 24 часов
    tomorrow = datetime.utcnow() + timedelta(days=1)
    
    expiring_deals = db.query(models.Deal).filter(
        models.Deal.deal_status == models.DealStatus.ACTIVE,
        models.Deal.option_expiry <= tomorrow,
        models.Deal.option_expiry > datetime.utcnow()
    ).all()
    
    notifications_sent = 0
    
    for deal in expiring_deals:
        # TODO: Отправить email/SMS/Telegram уведомление
        print(f"[NOTIFICATION] Deal #{deal.id} expires soon")
        notifications_sent += 1
    
    return {
        "success": True,
        "notifications_sent": notifications_sent
    }

# ============= ADMIN ENDPOINTS =============

@app.get("/api/admin/deals/pending")
async def get_pending_deals(db: Session = Depends(get_db)):
    """Получить сделки ожидающие обработки (admin)"""
    
    pending_deals = db.query(models.Deal).filter(
        models.Deal.deal_status == models.DealStatus.PENDING
    ).all()
    
    return pending_deals

@app.post("/api/admin/deals/check-expired")
async def check_expired_deals(db: Session = Depends(get_db)):
    """Проверить и перевести просроченные сделки в дефолт (cron job)"""
    
    now = datetime.utcnow()
    
    expired_deals = db.query(models.Deal).filter(
        models.Deal.deal_status == models.DealStatus.ACTIVE,
        models.Deal.option_expiry < now
    ).all()
    
    defaulted_count = 0
    
    for deal in expired_deals:
        deal.deal_status = models.DealStatus.DEFAULT
        defaulted_count += 1
        
        # Логирование
        audit_log = models.AuditLog(
            user_id=deal.user_id,
            action="deal_defaulted",
            details={
                "deal_id": deal.id,
                "reason": "option_expired",
                "expired_at": deal.option_expiry.isoformat()
            }
        )
        db.add(audit_log)
    
    db.commit()
    
    return {
        "success": True,
        "defaulted_count": defaulted_count,
        "timestamp": now.isoformat()
    }

@app.get("/api/admin/users/kyc-pending")
async def get_kyc_pending_users(db: Session = Depends(get_db)):
    """Получить пользователей с неподтвержденным KYC (admin)"""
    
    users = db.query(models.User).filter(
        models.User.passport_series.isnot(None),
        models.User.passport_verified == False
    ).all()
    
    return users

@app.post("/api/admin/users/{user_id}/verify-kyc")
async def verify_user_kyc(
    user_id: int,
    approved: bool,
    db: Session = Depends(get_db)
):
    """Подтвердить или отклонить KYC пользователя (admin)"""
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    user.passport_verified = approved
    
    audit_log = models.AuditLog(
        user_id=user_id,
        action="kyc_verification",
        details={
            "approved": approved,
            "verified_at": datetime.utcnow().isoformat()
        }
    )
    db.add(audit_log)
    
    db.commit()
    
    return {
        "success": True,
        "user_id": user_id,
        "approved": approved
    }
