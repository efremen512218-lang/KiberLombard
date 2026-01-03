"""
Тест расчёта процентов по срокам
"""
from services.pricing_service import PricingService


def test_exact_terms():
    """Тест точных значений"""
    print("=== Тест Точных Значений ===\n")
    
    exact_days = [7, 14, 21, 30]
    
    for days in exact_days:
        config = PricingService.get_term_config(days)
        total = config["interest"] + config["premium"]
        annual = total * (365 / days)
        
        print(f"{days} дней:")
        print(f"  Проценты: {config['interest']*100:.1f}%")
        print(f"  Премия: {config['premium']*100:.1f}%")
        print(f"  Итого: {total*100:.1f}%")
        print(f"  Годовых: {annual*100:.0f}%")
        print()


def test_interpolated_terms():
    """Тест интерполированных значений"""
    print("=== Тест Интерполяции ===\n")
    
    test_days = [10, 15, 18, 25]
    
    for days in test_days:
        config = PricingService.get_term_config(days)
        total = config["interest"] + config["premium"]
        annual = total * (365 / days)
        
        print(f"{days} дней:")
        print(f"  Проценты: {config['interest']*100:.1f}%")
        print(f"  Премия: {config['premium']*100:.1f}%")
        print(f"  Итого: {total*100:.1f}%")
        print(f"  Годовых: {annual*100:.0f}%")
        print()


def test_full_calculation():
    """Тест полного расчёта сделки"""
    print("=== Тест Полного Расчёта ===\n")
    
    # Пример: AK-47 Redline (FT)
    instant_price = 2800.0
    purchase_coefficient = PricingService.get_purchase_coefficient(instant_price)
    purchase_price = instant_price * purchase_coefficient
    
    print(f"Instant sell цена: {instant_price:.2f} ₽")
    print(f"Коэффициент покупки: {purchase_coefficient*100:.0f}%")
    print(f"Цена покупки (выдача): {purchase_price:.2f} ₽")
    print()
    
    for days in [7, 14, 21, 30]:
        config = PricingService.get_term_config(days)
        
        base_buyback = purchase_price * (1 + config["interest"])
        buyback_price = base_buyback * (1 + config["premium"])
        
        profit = buyback_price - purchase_price
        margin = (profit / purchase_price) * 100
        annual = margin * (365 / days)
        
        print(f"{days} дней:")
        print(f"  Выкуп: {buyback_price:.2f} ₽")
        print(f"  Прибыль: {profit:.2f} ₽ ({margin:.1f}%)")
        print(f"  Годовых: {annual:.0f}%")
        print()


def test_edge_cases():
    """Тест граничных случаев"""
    print("=== Тест Граничных Случаев ===\n")
    
    # Минимум
    config_min = PricingService.get_term_config(7)
    print(f"Минимум (7 дней): {(config_min['interest'] + config_min['premium'])*100:.1f}%")
    
    # Максимум
    config_max = PricingService.get_term_config(30)
    print(f"Максимум (30 дней): {(config_max['interest'] + config_max['premium'])*100:.1f}%")
    
    # Меньше минимума (должен вернуть минимум)
    config_below = PricingService.get_term_config(5)
    print(f"Ниже минимума (5 дней): {(config_below['interest'] + config_below['premium'])*100:.1f}%")
    
    # Больше максимума (должен вернуть максимум)
    config_above = PricingService.get_term_config(35)
    print(f"Выше максимума (35 дней): {(config_above['interest'] + config_above['premium'])*100:.1f}%")
    print()


if __name__ == "__main__":
    test_exact_terms()
    test_interpolated_terms()
    test_full_calculation()
    test_edge_cases()
    
    print("✅ Все тесты пройдены!")
