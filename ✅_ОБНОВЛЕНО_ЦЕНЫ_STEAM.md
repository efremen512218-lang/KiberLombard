# ✅ Обновлено: Привязка к ценам Steam Market

## Что изменилось

Убрали интеграцию с Lis-Skins и теперь используем **только реальные цены из Steam Market API**.

---

## Изменения в Backend

### 1. Схемы данных (`backend/schemas.py`)

**Убрали:**
- `lisskins_buy_price` 
- `lisskins_sell_price`
- `lisskins_sell_estimate`
- `lisskins_buy_total`

**Добавили:**
- `is_estimated` - флаг, что цена оценена по редкости (не реальная)

```python
class ItemWithPrice(SteamItem):
    market_price: float  # Цена Steam Market
    is_estimated: Optional[bool] = False  # Цена оценена по редкости

class InventoryResponse(BaseModel):
    steam_id: str
    items: List[ItemWithPrice]
    total_value: float  # Общая стоимость Steam Market
    last_updated: datetime
```

### 2. Сервис расчета цен (`backend/services/pricing_service.py`)

**Новая логика:**
```python
# Залог = 40% от Steam Market
loan_amount = market_total * 0.40

# Выкуп = Steam Market * 1.15 + премия опциона 25%
buyback_price = market_total * 1.15 + loan_amount * 0.25

# Прибыль если не выкупят (продаем на Steam Market)
profit_if_sell = market_total - loan_amount
```

**Убрали:**
- Расчет `lisskins_sell_estimate`
- Все упоминания Lis-Skins

### 3. API endpoints (`backend/main.py`)

**Обновлены:**
- `GET /api/inventory/{steam_id}` - возвращает только Steam Market цены
- `POST /api/quote` - расчет без Lis-Skins

**Пример ответа:**
```json
{
  "steam_id": "76561198000000000",
  "items": [
    {
      "assetid": "123",
      "name": "AK-47 | Redline",
      "market_price": 3500,
      "is_estimated": false
    }
  ],
  "total_value": 150000,
  "last_updated": "2024-12-05T10:00:00"
}
```

---

## Изменения в Frontend

### 1. Интерфейс предметов (`frontend/src/app/cabinet/inventory/page.tsx`)

**Убрали:**
- `lisskins_buy_price`
- `lisskins_sell_price`
- Отображение "Мгновенная покупка" (Lis-Skins)

**Обновили:**
- Показываем только Steam Market цену
- Добавили индикатор "⚠️ Оценка" для оцененных цен

**Новая логика расчета:**
```typescript
// Залог = 40% от Steam Market
const loanAmount = Math.round(selectedValue * 0.40)

// Выкуп = Steam Market * 1.15 + премия 25%
const buybackPrice = Math.round(selectedValue * 1.15 + loanAmount * 0.25)

// Прибыль если не выкупят (продаем на Steam Market)
const profitIfSell = Math.round(selectedValue - loanAmount)
```

### 2. Отображение цен

**Было:**
```
Steam: 3500 ₽
Мгновенно: 3920 ₽ (Lis-Skins)
Залог: 1400 ₽
```

**Стало:**
```
Steam: 3500 ₽
⚠️ Оценка (если is_estimated = true)
Залог: 1400 ₽
```

---

## Источники цен

### Steam Community Market API

**Endpoint:**
```
GET https://steamcommunity.com/market/priceoverview/
?appid=730
&currency=5
&market_hash_name={item_name}
```

**Ответ:**
```json
{
  "success": true,
  "lowest_price": "3 500,00 pуб.",
  "median_price": "3 600,00 pуб."
}
```

### Fallback: Оценка по редкости

Если Steam Market не вернул цену или цена < 10₽, используем оценку:

```python
rarity_prices = {
    "Contraband": 50000,
    "Covert": 5000,
    "Classified": 1000,
    "Restricted": 300,
    "Mil-Spec": 50,
    "Industrial Grade": 10,
    "Consumer Grade": 5
}
```

---

## Преимущества

✅ **Реальные цены** - только актуальные данные из Steam Market
✅ **Прозрачность** - пользователь видит рыночную цену
✅ **Простота** - нет зависимости от сторонних API
✅ **Надежность** - Steam Market API стабильнее

---

## Что дальше?

1. ✅ Убрали Lis-Skins из кода
2. ✅ Обновили расчет quote
3. ✅ Обновили фронтенд
4. 🔄 Перезапустить backend и frontend
5. 🔄 Проверить отображение цен в инвентаре

---

## Как проверить

1. Откройте инвентарь: http://localhost:3000/cabinet/inventory
2. Загрузите свой Steam ID
3. Проверьте что:
   - Показываются только Steam Market цены
   - Нет упоминаний Lis-Skins
   - Залог = 40% от Steam Market
   - Выкуп рассчитан правильно

---

**Дата:** 5 декабря 2024
**Статус:** ✅ Готово
