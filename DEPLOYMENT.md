# 🚀 Деплой КиберЛомбард CS2

## Требования

- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+
- Node.js 20+
- Python 3.11+
- Steam API ключ
- ЮKassa аккаунт (для платежей)
- SMS.ru аккаунт (для SMS)

## Локальная разработка

### 1. Клонировать репозиторий

```bash
git clone <repo-url>
cd cyber-lombard-cs2
```

### 2. Настроить переменные окружения

```bash
cp .env.example .env
# Заполнить все ключи в .env
```

### 3. Запустить БД

```bash
docker-compose up -d postgres redis
```

### 4. Мигрировать БД

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

### 5. Запустить Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API Docs: http://localhost:8000/docs

### 6. Запустить Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000

### 7. Запустить Steam Bot

```bash
cd steam-bot
npm install
npm run dev
```

Bot API: http://localhost:3001

## Production деплой

### Vercel (Frontend)

```bash
cd frontend
vercel --prod
```

Переменные окружения в Vercel:
- `NEXT_PUBLIC_API_URL` - URL backend API

### Render/Railway (Backend)

1. Создать новый Web Service
2. Подключить GitHub репозиторий
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Добавить переменные окружения из `.env.example`

### DigitalOcean/Hetzner (Steam Bot)

```bash
# На сервере
git clone <repo-url>
cd cyber-lombard-cs2/steam-bot
npm install --production
pm2 start src/index.js --name steam-bot
pm2 save
pm2 startup
```

### База данных

Рекомендуется:
- Supabase (PostgreSQL managed)
- Neon.tech (PostgreSQL serverless)
- DigitalOcean Managed Database

### Redis

- Upstash (Redis serverless)
- Redis Cloud
- DigitalOcean Managed Redis

## Настройка Steam Bot

### 1. Создать Steam аккаунт для бота

1. Зарегистрировать новый Steam аккаунт
2. Включить Steam Guard (мобильный аутентификатор)
3. Получить `shared_secret` и `identity_secret` через [steam-totp](https://github.com/DoctorMcKay/node-steam-totp)

### 2. Получить Steam API ключ

https://steamcommunity.com/dev/apikey

### 3. Настроить трейд-URL

https://steamcommunity.com/id/YOUR_BOT/tradeoffers/privacy

## Мониторинг

### Health checks

- Backend: `GET /health`
- Steam Bot: `GET /health`

### Логирование

- Backend: stdout (собирать через Docker logs)
- Steam Bot: stdout + файлы в `logs/`

### Алерты

Настроить уведомления для:
- Отключение Steam бота
- Ошибки трейдов
- Истечение сроков опционов (cron job)

## Безопасность

### Обязательно:

1. Изменить `JWT_SECRET` на случайную строку 32+ символов
2. Использовать HTTPS для всех сервисов
3. Настроить CORS только для своих доменов
4. Включить rate limiting (nginx/cloudflare)
5. Регулярные бэкапы БД
6. Хранить секреты в vault (не в .env файлах)

### Рекомендуется:

- WAF (Cloudflare, AWS WAF)
- DDoS защита
- Мониторинг подозрительной активности
- 2FA для админ-панели

## Cron Jobs

### Автоматический дефолт просроченных сделок

```bash
# Каждый час
0 * * * * curl -X POST https://api.yourdomain.com/api/admin/deals/check-expired
```

### Обновление рыночных цен

```bash
# Каждые 6 часов
0 */6 * * * curl -X POST https://api.yourdomain.com/api/admin/prices/update
```

## Масштабирование

### Горизонтальное:

- Backend: несколько инстансов за load balancer
- Steam Bot: несколько ботов (round-robin)
- Redis: Redis Cluster

### Вертикальное:

- Увеличить ресурсы БД при росте нагрузки
- Кеширование частых запросов (inventory, prices)

## Поддержка

Документация API: https://api.yourdomain.com/docs
Техподдержка: support@cyberlombard.ru
