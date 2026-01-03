from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from models import DealStatus, TradeStatus

# User schemas
class UserBase(BaseModel):
    steam_id: str
    steam_username: Optional[str] = None
    steam_avatar: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserKYC(BaseModel):
    phone: str
    passport_series: str
    passport_number: str
    passport_issued_by: str
    passport_department_code: str

class User(UserBase):
    id: int
    phone: Optional[str] = None
    phone_verified: bool = False
    passport_verified: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True

# Item schemas
class SteamItem(BaseModel):
    assetid: str
    market_hash_name: str
    icon_url: str
    name: str
    type: str
    rarity: Optional[str] = None
    float_value: Optional[float] = None
    
class ItemWithPrice(SteamItem):
    market_price: float  # Цена Steam Market
    is_estimated: Optional[bool] = False  # Цена оценена по редкости (не реальная)

# Quote schemas
class QuoteRequest(BaseModel):
    steam_id: str
    asset_ids: List[str]  # Выбранные предметы
    option_days: int = Field(default=14, ge=7, le=30)

class QuoteResponse(BaseModel):
    market_total: float  # Рыночная стоимость (Steam Market)
    loan_amount: float  # 30% от Steam Market
    buyback_price: float  # 60% от Steam Market
    profit_if_buyback: Optional[float] = 0.0  # Прибыль если выкупят
    profit_if_sell: Optional[float] = 0.0  # Прибыль если не выкупят (продажа на Lis-Skins)
    option_expiry: datetime
    items: List[ItemWithPrice]
    
    breakdown: dict = Field(default_factory=dict)  # Детали расчета (включая проценты)

# KYC snapshot для сделки
class KYCSnapshot(BaseModel):
    full_name: Optional[str] = None
    passport_series: Optional[str] = None
    passport_number: Optional[str] = None
    birth_date: Optional[str] = None
    department_code: Optional[str] = None
    registration_address: Optional[str] = None
    phone: Optional[str] = None

# Deal schemas
class DealCreate(BaseModel):
    quote_request: QuoteRequest
    sms_code: str
    accept_terms: bool = True
    skip_verification: bool = False  # DEV MODE: пропустить верификацию
    kyc_data: Optional[KYCSnapshot] = None  # Паспортные данные
    
    @validator('accept_terms')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('Необходимо принять условия договора')
        return v

class DealResponse(BaseModel):
    id: int
    user_id: int
    market_total: float
    loan_amount: float
    buyback_price: float
    created_at: datetime
    option_expiry: datetime
    deal_status: DealStatus
    items_snapshot: List[dict]
    kyc_snapshot: Optional[dict] = None
    initial_trade_url: Optional[str] = None
    contract_pdf_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class DealDetail(DealResponse):
    user: User
    buyback_at: Optional[datetime] = None
    payout_transaction_id: Optional[str] = None
    kyc_snapshot: Optional[dict] = None
    
    # Вычисляемые поля
    is_expired: bool = False
    can_buyback: bool = False
    days_left: Optional[int] = None

# Trade schemas
class TradeCreate(BaseModel):
    deal_id: int
    items: List[dict]

class TradeResponse(BaseModel):
    id: int
    deal_id: int
    trade_offer_id: str
    trade_offer_url: str
    status: TradeStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# SMS schemas
class SMSRequest(BaseModel):
    phone: str
    purpose: str  # "phone_verify", "deal_sign", "buyback"

class SMSVerify(BaseModel):
    phone: str
    code: str
    purpose: str

# Payment schemas
class PaymentCreate(BaseModel):
    deal_id: int
    amount: float
    return_url: str

class PaymentResponse(BaseModel):
    payment_id: str
    confirmation_url: str
    status: str

# Inventory schemas
class InventoryResponse(BaseModel):
    steam_id: str
    items: List[ItemWithPrice]
    total_value: float  # Общая стоимость Steam Market
    last_updated: datetime
