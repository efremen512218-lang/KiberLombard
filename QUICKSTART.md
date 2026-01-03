# 🚀 Быстрый старт КиберЛомбард CS2

## За 5 минут до первой сделки

### 1. Установка зависимостей

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install

# Steam Bot
cd steam-bot
npm install
```

### 2. Настройка .env

```bash
# Корневой .env
cp .env.example .env

# Минимальные настройки для локальной разработки:
STEAM_API_KEY=your_key_here  # Получить на https://steamcommunity.com/dev/apikey
DATABASE_URL=postgresql://admin:dev_password_change_in_prod@localhost:5432/cyberlombard
```

### 3. Запуск БД

```bash
docker-compose up -d postgres redis
```

### 4. Инициализация БД

```bash
cd backend
python -c "from database import engine; from models import Base; Base.metadata.create_all(engine)"
```

### 5. Запуск всех сервисов

**Терминал 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Терминал 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Терминал 3 - Steam Bot (опционально):**
```bash
cd steam-bot
npm run dev
```

### 6. Открыть приложение

Frontend: http://localhost:3000
Backend API Docs: http://localhost:8000/docs

## Тестирование без Steam

### Mock данные

Backend автоматически возвращает тестовые данные если Steam API недоступен:

```python
# В services/steam_service.py уже есть fallback на mock данные
```

### Тестовый flow

1. Открыть http://localhost:3000
2. Нажать "Войти через Steam" (будет mock авторизация)
3. Перейти в "Инвентарь" - увидите тестовые скины
4. Выбрать скины → "Продолжить"
5. Ввести телефон → получить SMS-код (в консоли backend)
6. Подписать договор → создать сделку

## Проверка работоспособности

### Health checks

```bash
# Backend
curl http://localhost:8000/health

# Steam Bot
curl http://localhost:3001/health
```

### Тестовые API запросы

```bash
# Получить инвентарь (mock)
curl http://localhost:8000/api/inventory/76561198000000000

# Рассчитать quote
curl -X POST http://localhost:8000/api/quote \
  -H "Content-Type: application/json" \
  -d '{
    "steam_id": "76561198000000000",
    "asset_ids": ["123", "456"],
    "option_days": 14
  }'
```

## Частые проблемы

### "Connection refused" при запуске

**Решение**: Убедитесь что PostgreSQL и Redis запущены:
```bash
docker-compose ps
```

### "Steam API key invalid"

**Решение**: Получите ключ на https://steamcommunity.com/dev/apikey и добавьте в .env

### Frontend не подключается к Backend

**Решение**: Проверьте NEXT_PUBLIC_API_URL в frontend/.env.local:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Steam Bot не подключается

**Решение**: Для разработки можно работать без бота. Трейды будут в статусе "PENDING".

## Следующие шаги

1. Изучить [DEPLOYMENT.md](DEPLOYMENT.md) для production деплоя
2. Прочитать [LEGAL.md](LEGAL.md) для юридической защиты
3. Настроить реальные Steam боты
4. Интегрировать платежную систему (ЮKassa)
5. Настроить SMS-провайдера (SMS.ru)

## Поддержка

- Документация API: http://localhost:8000/docs
- GitHub Issues: [создать issue]
- Email: dev@cyberlombard.ru
