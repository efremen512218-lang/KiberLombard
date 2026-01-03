import pytest
from services.pricing_service import PricingService

def test_calculate_quote():
    """Тест расчета условий сделки"""
    items = [
        {"market_hash_name": "AK-47 | Redline", "market_price": 1000},
        {"market_hash_name": "AWP | Asiimov", "market_price": 5000},
    ]
    
    quote = PricingService.calculate_quote(items, option_days=14)
    
    assert quote["market_total"] == 6000
    assert quote["loan_amount"] == 3900  # 65% от 6000
    assert quote["buyback_price"] == 7875  # 6000 * 1.15 + 3900 * 0.25
    
def test_kyc_required():
    """Тест проверки необходимости KYC"""
    assert PricingService.check_kyc_required(10000) == False
    assert PricingService.check_kyc_required(20000) == True
    
def test_calculate_profit():
    """Тест расчета прибыли"""
    deal = {
        "market_total": 10000,
        "loan_amount": 6500,
        "buyback_price": 13625
    }
    
    profit = PricingService.calculate_profit(deal)
    
    assert profit["profit_if_buyback"] == 7125  # 13625 - 6500
    assert profit["profit_if_default"] == 3500  # 10000 - 6500
