# 🔌 API Интеграция - Получение Цен

## 1. Market.CSGO API

### Получение API Ключа

1. **Регистрация:**
   - Перейти на https://market.csgo.com/
   - Войти через Steam
   - Перейти в настройки аккаунта

2. **Создание API ключа:**
   - Раздел "API"
   - Создать новый ключ
   - Скопировать ключ (показывается один раз!)

3. **Добавить в .env:**
   ```env
   MARKET_CSGO_API_KEY=your_api_key_here
   ```

### API Endpoints

#### 1. Список всех цен
```
GET https://market.csgo.com/api/v2/prices/RUB.json
```

**Ответ:**
```json
{
  "success": true,
  "time": 1724318846,
  "currency": "RUB",
  "items": {
    "AK-47 | Redline (Field-Tested)": {
      "price": 2800,
      "avg_price": 2900,
      "popularity_7d": 150
    }
  }
}
```

#### 2. Цены с buy-ордерами (по classid/instanceid)
```
GET https://market.csgo.com/api/v2/prices/class_instance/RUB.json
```

**Ответ:**
```json
{
  "success": true,
  "currency": "RUB",
  "items": {
    "1434515088_0": {
      "price": "2800",
      "buy_order": "2600",
      "avg_price": "2900",
      "market_hash_name": "AK-47 | Redline (Field-Tested)"
    }
  }
}
```

#### 3. История цен конкретного предмета
```
GET https://market.csgo.com/api/v2/get-list-items-info?key={API_KEY}&list_hash_name[]={market_hash_name}
```

**Параметры:**
- `key` - API ключ
- `list_hash_name[]` - market_hash_name предмета (можно несколько)

**Ответ:**
```json
{
  "data": {
    "AK-47 | Redline (Field-Tested)": {
      "min": {"RUB": 2700},
      "max": {"RUB": 2900},
      "average": {"RUB": 2800},
      "average7d": {"RUB": 2850},
      "sales7d": {"RUB": 150}
    }
  }
}
```

### Rate Limits
- **Без ключа:** 1 запрос в 5 секунд
- **С ключом:** 5 запросов в секунду
- **Рекомендация:** Кешировать на 1 час

---

## 2. Lis-Skins API

### Статус: Требуется Исследование

**Проблема:** Публичная документация API не найдена

**Возможные Варианты:**

#### Вариант 1: Обратный Инжиниринг
Изучить запросы на сайте lis-skins.ru:
1. Открыть DevTools (F12)
2. Вкладка Network
3. Выбрать предмет для продажи
4. Найти API запросы
5. Скопировать endpoints и параметры

#### Вариант 2: Связаться с Поддержкой
1. Написать в поддержку lis-skins.ru
2. Запросить API документацию
3. Объяснить цель использования (интеграция для бизнеса)

#### Вариант 3: Использовать Альтернативы
Пока нет API Lis-Skins, использовать:
- **market.csgo** - как основной источник instant цен
- **Steam Market** - как справочный
- **CSGOFloat** - альтернативный источник

### Предполагаемая Структура API

На основе анализа сайта, вероятная структура:

```
GET https://lis-skins.ru/api/v1/prices
Authorization: Bearer {API_KEY}

Response:
{
  "items": {
    "AK-47 | Redline (Field-Tested)": {
      "instant_sell": 2800,
      "instant_buy": 3200,
      "available": true
    }
  }
}
```

---

## 3. Текущая Реализация (Временная)

### market_csgo_service.py

```python
"""
Интеграция с market.csgo для получения цен
"""
import httpx
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta
import os


class MarketCSGOService:
    """Сервис для получения цен с market.csgo"""
    
    API_URL = "https://market.csgo.com/api/v2"
    API_KEY = os.getenv("MARKET_CSGO_API_KEY", "")
    
    # Кеш цен
    _cache: Dict[str, tuple[float, datetime]] = {}
    _cache_ttl = timedelta(hours=1)
    
    @staticmethod
    async def get_prices(market_hash_names: List[str]) -> Dict[str, float]:
        """
        Получить цены с market.csgo
        
        Args:
            market_hash_names: Список названий предметов
            
        Returns:
            Dict с ценами в рублях
        """
        prices = {}
        uncached = []
        
        # Проверяем кеш
        for name in market_hash_names:
            cached = MarketCSGOService._get_from_cache(name)
            if cached > 0:
                prices[name] = cached
            else:
                uncached.append(name)
        
        if not uncached:
            return prices
        
        print(f"[MARKET.CSGO] Загружаем {len(uncached)} цен")
        
        try:
            # Получаем все цены одним запросом
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{MarketCSGOService.API_URL}/prices/RUB.json"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        items = data.get("items", {})
                        
                        for name in uncached:
                            if name in items:
                                # Используем минимальную цену (instant sell)
                                price = float(items[name].get("price", 0))
                                if price > 0:
                                    prices[name] = price
                                    MarketCSGOService._save_to_cache(name, price)
        
        except Exception as e:
            print(f"[MARKET.CSGO] Ошибка: {e}")
        
        # Для предметов без цены возвращаем 0
        for name in market_hash_names:
            if name not in prices:
                prices[name] = 0.0
        
        successful = len([p for p in prices.values() if p > 0])
        print(f"[MARKET.CSGO] Получено {successful}/{len(market_hash_names)} цен")
        
        return prices
    
    @staticmethod
    async def get_item_details(market_hash_names: List[str]) -> Dict[str, dict]:
        """
        Получить детальную информацию о предметах
        
        Требует API ключ!
        """
        if not MarketCSGOService.API_KEY:
            print("[MARKET.CSGO] API ключ не установлен")
            return {}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Формируем параметры
                params = {
                    "key": MarketCSGOService.API_KEY
                }
                for name in market_hash_names:
                    params[f"list_hash_name[]"] = name
                
                response = await client.get(
                    f"{MarketCSGOService.API_URL}/get-list-items-info",
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {})
        
        except Exception as e:
            print(f"[MARKET.CSGO] Ошибка получения деталей: {e}")
        
        return {}
    
    @staticmethod
    def _get_from_cache(name: str) -> float:
        """Получить из кеша"""
        if name in MarketCSGOService._cache:
            price, timestamp = MarketCSGOService._cache[name]
            if datetime.now() - timestamp < MarketCSGOService._cache_ttl:
                return price
        return 0.0
    
    @staticmethod
    def _save_to_cache(name: str, price: float):
        """Сохранить в кеш"""
        MarketCSGOService._cache[name] = (price, datetime.now())
    
    @staticmethod
    def clear_cache():
        """Очистить кеш"""
        MarketCSGOService._cache.clear()
        print("[MARKET.CSGO] Кеш очищен")
```

---

## 4. Стратегия Получения Цен

### Приоритет Источников

1. **market.csgo** (основной)
   - Есть API
   - Есть instant цены
   - Хорошая документация
   - ✅ Используем СЕЙЧАС

2. **Lis-Skins** (желательный)
   - Нет публичного API
   - Нужно исследовать
   - ⏳ В разработке

3. **Steam Market** (справочный)
   - Есть API
   - Только рыночные цены (не instant)
   - ✅ Используем для отображения

### Текущая Логика

```python
# 1. Получаем цены из всех источников
steam_prices = await SteamPriceService.get_prices(items)
market_prices = await MarketCSGOService.get_prices(items)
lis_prices = await LisSkinsService.get_prices(items)  # Пока демо

# 2. Определяем instant цену
for item in items:
    steam = steam_prices.get(item, 0)
    market = market_prices.get(item, 0)
    lis = lis_prices.get(item, 0)
    
    # Instant цена = минимум из доступных instant источников
    instant_sources = []
    if market > 0:
        instant_sources.append(market)
    if lis > 0:
        instant_sources.append(lis)
    
    instant_price = min(instant_sources) if instant_sources else 0
    
    # Принимаем только если есть instant цена >= 20₽
    is_acceptable = instant_price >= 20
```

---

## 5. План Действий

### Немедленно (Сегодня)
- [x] Изучить market.csgo API
- [x] Создать документацию
- [ ] Получить API ключ market.csgo
- [ ] Протестировать реальные запросы

### Краткосрочно (Эта Неделя)
- [ ] Исследовать Lis-Skins API (reverse engineering)
- [ ] Связаться с поддержкой Lis-Skins
- [ ] Реализовать реальную интеграцию market.csgo
- [ ] Обновить price_aggregator.py

### Среднесрочно (Следующая Неделя)
- [ ] Получить доступ к Lis-Skins API
- [ ] Реализовать интеграцию Lis-Skins
- [ ] Протестировать с реальными данными
- [ ] Оптимизировать кеширование

---

## 6. Альтернативные Источники

### CSGOFloat API
```
GET https://csgofloat.com/api/v1/listings
```
- Есть instant цены
- Требует регистрацию
- Хорошая документация

### CSGOBackpack API
```
GET https://csgobackpack.net/api/GetItemsList/v2/
```
- Средние цены
- Бесплатный
- Простой API

### SkinBaron API
```
GET https://skinbaron.de/api/v1/Prices
```
- Европейский рынок
- Требует API ключ
- Цены в EUR

---

## 7. Тестирование

### Тест market.csgo API

```python
# backend/test_market_csgo.py
import asyncio
from services.market_csgo_service import MarketCSGOService


async def test_market_csgo():
    """Тест получения цен с market.csgo"""
    
    items = [
        "AK-47 | Redline (Field-Tested)",
        "AWP | Asiimov (Field-Tested)",
        "M4A4 | Howl (Field-Tested)",
        "Desert Eagle | Blaze (Factory New)"
    ]
    
    print("Тестируем market.csgo API...")
    prices = await MarketCSGOService.get_prices(items)
    
    print("\nРезультаты:")
    for item, price in prices.items():
        print(f"{item}: {price}₽")
    
    # Тест деталей (требует API ключ)
    if MarketCSGOService.API_KEY:
        print("\nПолучаем детали...")
        details = await MarketCSGOService.get_item_details(items[:2])
        print(details)


if __name__ == "__main__":
    asyncio.run(test_market_csgo())
```

**Запуск:**
```bash
cd backend
python test_market_csgo.py
```

---

## 8. Мониторинг и Логирование

### Метрики для Отслеживания

```python
# Успешность запросов
api_success_rate = successful_requests / total_requests

# Среднее время ответа
avg_response_time = sum(response_times) / len(response_times)

# Cache hit rate
cache_hit_rate = cache_hits / total_requests

# Доступность цен
price_availability = items_with_price / total_items
```

### Алерты

- ⚠️ API недоступен > 5 минут
- ⚠️ Cache hit rate < 70%
- ⚠️ Доступность цен < 80%
- ⚠️ Время ответа > 5 секунд

---

## Итого

### Что Работает Сейчас
✅ market.csgo API (без ключа, базовые цены)  
✅ Steam Market API (справочные цены)  
✅ Кеширование на 1 час  
✅ Fallback логика  

### Что Нужно Сделать
🔲 Получить API ключ market.csgo  
🔲 Исследовать Lis-Skins API  
🔲 Реализовать реальные интеграции  
🔲 Протестировать с production данными  

### Временное Решение
Используем **market.csgo** как основной источник instant цен вместо Lis-Skins до получения их API.
