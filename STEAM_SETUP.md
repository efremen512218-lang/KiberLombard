# 🎮 Настройка Steam API и Bot

## 1. Получение Steam API Key

### Шаги:

1. Войти в Steam аккаунт
2. Перейти на https://steamcommunity.com/dev/apikey
3. Указать домен (например: `localhost` для разработки)
4. Скопировать API Key
5. Добавить в `.env`:
   ```
   STEAM_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

### Лимиты:

- 100,000 запросов в день
- Rate limit: ~1 запрос в секунду на endpoint
- Для production рекомендуется несколько ключей

## 2. Создание Steam Bot аккаунта

### Требования:

- Новый Steam аккаунт (не основной!)
- Потрачено минимум $5 (для снятия ограничений)
- Включен Steam Guard (мобильный аутентификатор)
- Trade URL публичный

### Шаги создания:

1. **Регистрация аккаунта:**
   - Создать новый Steam аккаунт
   - Подтвердить email
   - Пополнить кошелек на $5+
   - Купить любую игру (например, CS2)

2. **Настройка Steam Guard:**
   - Скачать Steam Mobile App
   - Включить Steam Guard
   - Подождать 7 дней (ограничение Steam)

3. **Получение секретов для бота:**

   **Вариант A: Через WinAuth (Windows)**
   ```
   1. Скачать WinAuth: https://github.com/winauth/winauth
   2. Add Authenticator → Steam
   3. Войти в аккаунт бота
   4. Скопировать:
      - Shared Secret
      - Identity Secret
   ```

   **Вариант B: Через steam-totp (Node.js)**
   ```bash
   npm install -g steam-totp
   steam-totp --setup
   # Следовать инструкциям
   ```

4. **Настройка Trade URL:**
   ```
   1. Перейти: https://steamcommunity.com/id/YOUR_BOT/tradeoffers/privacy
   2. Создать Trade URL
   3. Сделать профиль публичным
   4. Инвентарь публичным
   ```

5. **Добавить в .env:**
   ```
   STEAM_BOT_USERNAME=your_bot_username
   STEAM_BOT_PASSWORD=your_bot_password
   STEAM_SHARED_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxx
   STEAM_IDENTITY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

## 3. Тестирование бота

### Запуск:

```bash
cd steam-bot
npm install
npm run dev
```

### Проверка подключения:

```bash
# Health check
curl http://localhost:3001/health

# Должен вернуть:
{
  "status": "ok",
  "steam_connected": true,
  "timestamp": "2025-12-05T..."
}
```

### Логи:

Успешное подключение:
```
[BOT] Подключение к Steam...
[BOT] ✅ Успешный вход в Steam
[BOT] ✅ Web сессия получена
[BOT] 🚀 API запущен на порту 3001
```

## 4. Множественные боты (Production)

### Зачем нужно:

- Распределение нагрузки
- Резервирование (если один бан)
- Разные боты для разных ценовых категорий

### Настройка:

1. **Создать 3-5 бот-аккаунтов**
2. **Конфигурация в .env:**
   ```
   # Bot 1
   STEAM_BOT_1_USERNAME=bot1_username
   STEAM_BOT_1_PASSWORD=bot1_password
   STEAM_BOT_1_SHARED_SECRET=xxx
   STEAM_BOT_1_IDENTITY_SECRET=xxx
   
   # Bot 2
   STEAM_BOT_2_USERNAME=bot2_username
   ...
   ```

3. **Запуск нескольких инстансов:**
   ```bash
   # PM2 ecosystem
   pm2 start ecosystem.config.js
   ```

4. **Load balancing через Redis:**
   ```javascript
   // Выбор бота из пула
   const availableBot = await redis.lpop('bot_queue')
   ```

## 5. Steam OpenID (авторизация пользователей)

### Настройка в Backend:

```python
# main.py
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

@app.get("/auth/steam")
async def steam_login(request: Request):
    return_url = "http://localhost:3000/auth/steam/callback"
    
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': return_url,
        'openid.realm': 'http://localhost:3000',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }
    
    url = 'https://steamcommunity.com/openid/login?' + urlencode(params)
    return RedirectResponse(url)

@app.get("/auth/steam/callback")
async def steam_callback(request: Request):
    # Валидация OpenID response
    # Извлечение Steam ID
    # Создание JWT токена
    pass
```

### Настройка в Frontend:

```typescript
// pages/auth/steam/callback.tsx
export default function SteamCallback() {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    
    // Отправить на backend для валидации
    fetch('/api/auth/steam/verify', {
      method: 'POST',
      body: JSON.stringify({ params: Object.fromEntries(params) })
    })
    .then(res => res.json())
    .then(data => {
      // Сохранить токен
      localStorage.setItem('token', data.token)
      router.push('/cabinet')
    })
  }, [])
  
  return <div>Авторизация...</div>
}
```

## 6. Частые проблемы

### "Invalid API Key"

**Причина:** Неверный или не активированный ключ

**Решение:**
1. Проверить ключ на https://steamcommunity.com/dev/apikey
2. Убедиться что домен указан правильно
3. Подождать 5 минут после создания

### "Bot не подключается"

**Причина:** Неверные credentials или 2FA

**Решение:**
1. Проверить username/password
2. Проверить shared_secret (генерировать новый код: `steam-totp <secret>`)
3. Убедиться что Steam Guard включен
4. Проверить логи: `npm run dev`

### "Trade offer declined automatically"

**Причина:** Ограничения Steam

**Решение:**
1. Аккаунт бота должен быть старше 7 дней с Steam Guard
2. Потрачено минимум $5
3. Нет VAC/Trade банов
4. Инвентарь публичный

### "Rate limit exceeded"

**Причина:** Слишком много запросов к Steam API

**Решение:**
1. Добавить задержки между запросами (1-2 сек)
2. Кешировать результаты в Redis
3. Использовать несколько API ключей

## 7. Безопасность

### Защита credentials:

```bash
# НЕ коммитить в Git!
echo ".env" >> .gitignore
echo "steam-bot/.env" >> .gitignore

# Использовать secrets manager в production
# AWS Secrets Manager / HashiCorp Vault
```

### Мониторинг:

```javascript
// Алерты при отключении бота
setInterval(async () => {
  if (!client.steamID) {
    await sendAlert('Steam bot disconnected!')
    client.logOn(loginOptions) // Переподключение
  }
}, 60000) // Каждую минуту
```

### Backup аккаунтов:

- Хранить credentials в безопасном месте
- Иметь 2-3 резервных бота
- Регулярно проверять статус ботов

## 8. Тестирование

### Тестовый трейд:

```bash
# Создать тестовый трейд
curl -X POST http://localhost:3001/api/trade/create \
  -H "Content-Type: application/json" \
  -d '{
    "deal_id": 1,
    "partner_steam_id": "76561198000000000",
    "items": [
      {"assetid": "123456789"}
    ]
  }'

# Проверить в Steam:
# https://steamcommunity.com/profiles/YOUR_BOT_ID/tradeoffers/
```

### Mock режим (без реального Steam):

```javascript
// steam-bot/src/index.js
const MOCK_MODE = process.env.MOCK_MODE === 'true'

if (MOCK_MODE) {
  console.log('[BOT] 🧪 MOCK MODE - Steam не подключен')
  // Эмуляция трейдов
}
```

## 9. Production Checklist

- [ ] API ключ получен и работает
- [ ] Минимум 3 бот-аккаунта настроены
- [ ] Все боты прошли 7-дневный период Steam Guard
- [ ] Trade URLs публичные
- [ ] Credentials в secrets manager (не в .env)
- [ ] Мониторинг и алерты настроены
- [ ] Backup план при бане ботов
- [ ] Rate limiting настроен
- [ ] Логирование всех трейдов

## 10. Полезные ссылки

- Steam API Docs: https://developer.valvesoftware.com/wiki/Steam_Web_API
- Steam OpenID: https://steamcommunity.com/dev
- steam-user: https://github.com/DoctorMcKay/node-steam-user
- steam-tradeoffer-manager: https://github.com/DoctorMcKay/node-steam-tradeoffer-manager
- WinAuth: https://github.com/winauth/winauth
