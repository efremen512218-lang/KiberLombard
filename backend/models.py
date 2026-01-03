from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class DealStatus(str, enum.Enum):
    PENDING = "PENDING"  # Ожидает трейда
    ACTIVE = "ACTIVE"    # Активна, скины получены
    BUYBACK = "BUYBACK"  # Выкуплена клиентом
    DEFAULT = "DEFAULT"  # Дефолт, срок истек
    CANCELLED = "CANCELLED"  # Отменена

class TradeStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    steam_id = Column(String, unique=True, index=True, nullable=False)
    steam_username = Column(String)
    steam_avatar = Column(String)
    trade_url = Column(String)  # Полный trade URL
    trade_token = Column(String)  # Токен для трейдов
    
    # KYC данные (115-ФЗ)
    phone = Column(String, unique=True, index=True)
    phone_verified = Column(Boolean, default=False)
    
    passport_series = Column(String)
    passport_number = Column(String)
    passport_issued_by = Column(String)
    passport_department_code = Column(String)
    passport_photo_url = Column(String)
    passport_verified = Column(Boolean, default=False)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), onupdate=func.now())
    is_blocked = Column(Boolean, default=False)
    
    # Связи
    deals = relationship("Deal", back_populates="user")

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Финансовые условия (фиксируются при создании)
    market_total = Column(Float, nullable=False)  # Рыночная цена на момент сделки
    loan_amount = Column(Float, nullable=False)  # Сумма выплаты клиенту
    buyback_price = Column(Float, nullable=False)  # Цена выкупа (фикс)
    
    # Сроки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    option_expiry = Column(DateTime(timezone=True), nullable=False)  # Срок опциона
    buyback_at = Column(DateTime(timezone=True))  # Когда выкуплено
    
    # Статус
    deal_status = Column(Enum(DealStatus), default=DealStatus.PENDING, nullable=False)
    
    # Скины (snapshot на момент сделки)
    items_snapshot = Column(JSON, nullable=False)  # [{market_hash_name, float, price, assetid}]
    
    # KYC данные на момент сделки
    kyc_snapshot = Column(JSON)  # {full_name, passport_series, passport_number, registration_address, phone}
    
    # Трейды
    initial_trade_id = Column(String)  # ID трейда получения скинов
    initial_trade_url = Column(String)
    buyback_trade_id = Column(String)  # ID обратного трейда
    
    # Договор
    contract_pdf_url = Column(String)
    signature_sms_code = Column(String)  # Хеш SMS-кода (ПЭП)
    signature_timestamp = Column(DateTime(timezone=True))
    
    # Платежи
    payout_transaction_id = Column(String)  # ID выплаты клиенту
    buyback_payment_id = Column(String)  # ID оплаты выкупа
    
    # Связи
    user = relationship("User", back_populates="deals")
    trades = relationship("SteamTrade", back_populates="deal")

class SteamTrade(Base):
    __tablename__ = "steam_trades"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    
    trade_offer_id = Column(String, unique=True, index=True)
    trade_offer_url = Column(String)
    
    is_incoming = Column(Boolean, default=True)  # True = получаем скины, False = отдаем
    
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING)
    
    items_json = Column(JSON)  # Список предметов в трейде
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True))
    
    # Связи
    deal = relationship("Deal", back_populates="trades")

class SMSVerification(Base):
    __tablename__ = "sms_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False)  # Хешированный код
    purpose = Column(String, nullable=False)  # "phone_verify", "deal_sign", "buyback"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True))
    
    is_used = Column(Boolean, default=False)

class KYCVerification(Base):
    __tablename__ = "kyc_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # ID внешнего провайдера
    verification_id = Column(String, unique=True, index=True)
    
    # Статус
    status = Column(String, default="pending")  # pending, passed, failed
    
    # Данные паспорта
    full_name = Column(String)
    birth_date = Column(String)
    passport_series = Column(String)
    passport_number = Column(String)
    issued_by = Column(Text)
    issue_date = Column(String)
    department_code = Column(String)
    photo_url = Column(String)
    
    # Ответ провайдера
    provider_response = Column(JSON)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True))

class DealSignature(Base):
    __tablename__ = "deal_signatures"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Данные подписанта
    phone = Column(String, nullable=False)
    
    # Параметры подписи
    signature_code_hash = Column(String, nullable=False)
    signature_timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Технические данные
    ip_address = Column(String)
    user_agent = Column(Text)
    
    # Договор
    contract_hash = Column(String, nullable=False)  # SHA-256
    contract_version = Column(String, default="v1.0")
    contract_pdf_url = Column(String)
    
    # Связь с KYC
    kyc_verification_id = Column(Integer, ForeignKey("kyc_verifications.id"))
    
    # Согласие с условиями
    terms_accepted_at = Column(DateTime(timezone=True), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SBPPayout(Base):
    __tablename__ = "sbp_payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False)
    
    # ID внешнего провайдера
    payout_id = Column(String, unique=True, index=True)
    
    # Данные выплаты
    phone = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    
    # Статус
    status = Column(String, default="pending")  # pending, processing, completed, failed
    
    # Ошибки
    error_code = Column(String)
    error_message = Column(Text)
    
    # Ответ провайдера
    provider_response = Column(JSON)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    deal_id = Column(Integer, ForeignKey("deals.id"))
    
    action = Column(String, nullable=False)  # "deal_created", "trade_accepted", etc.
    details = Column(JSON)
    
    ip_address = Column(String)
    user_agent = Column(Text)
    session_id = Column(String)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
