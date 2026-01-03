from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Dict


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./cyberlombard.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Steam
    steam_api_key: str = ""
    
    # Production
    production_domain: str = ""  # e.g. "yourdomain.com"
    
    # JWT
    jwt_secret: str = "change_this_in_production_min_32_chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # Payment
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    
    # SMS
    sms_provider: str = "fake"  # "sms.ru", "smsc.ru", "fake"
    sms_api_key: str = ""
    sms_code_length: int = 6
    sms_code_ttl_seconds: int = 300  # 5 минут
    sms_rate_limit_seconds: int = 60  # 1 минута между отправками
    
    # KYC
    kyc_provider: str = "fake"  # "sumsub", "fake"
    kyc_api_key: str = ""
    kyc_timeout_seconds: int = 300  # 5 минут на проверку
    
    # СБП
    sbp_provider: str = "fake"  # "modulbank", "fake"
    sbp_api_key: str = ""
    sbp_min_amount: float = 100.0
    sbp_max_amount: float = 600000.0
    
    # === ЦЕНЫ ===
    
    # Минимальная instant цена для приёма предмета
    min_instant_price: float = 20.0
    
    # Максимальный возраст цен (часы)
    max_price_age_hours: int = 1
    
    # Пороги для процентов выдачи
    # Формат: [(max_price, percent), ...]
    loan_tiers: str = "500:0.60,5000:0.65,inf:0.70"
    
    # === СРОКИ ВЫКУПА ===
    
    # Диапазон сроков
    min_term_days: int = 7
    max_term_days: int = 30
    
    # Конфигурация процентов по срокам
    # Формат: "days:interest:premium,..."
    buyback_terms: str = "7:0.10:0.05,14:0.15:0.07,21:0.20:0.09,30:0.25:0.10"
    
    # === ТРЕЙДЫ ===
    
    trade_timeout_hours: int = 48  # 2 дня на принятие
    
    # === ЮРИДИЧЕСКОЕ ===
    
    contract_version: str = "v1.0"
    terms_version: str = "2025-12-01"
    
    # === ИНТЕГРАЦИИ ===
    
    # Lis-Skins
    lis_skins_api_url: str = "https://lis-skins.ru/api/v2"
    lis_skins_api_key: str = ""
    
    # market.csgo
    market_csgo_api_url: str = "https://market.csgo.com/api/v2"
    market_csgo_api_key: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"
    
    def get_loan_tiers(self) -> List[Dict]:
        """Парсинг loan_tiers из строки"""
        tiers = []
        for tier in self.loan_tiers.split(","):
            max_price, percent = tier.split(":")
            tiers.append({
                "max": float('inf') if max_price == "inf" else float(max_price),
                "percent": float(percent)
            })
        return tiers
    
    def get_buyback_terms(self) -> Dict[int, Dict]:
        """Парсинг buyback_terms из строки"""
        terms = {}
        for term in self.buyback_terms.split(","):
            days, interest, premium = term.split(":")
            terms[int(days)] = {
                "interest": float(interest),
                "premium": float(premium)
            }
        return terms


@lru_cache()
def get_settings():
    return Settings()
