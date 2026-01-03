@echo off
echo ========================================
echo   КиберЛомбард - Первоначальная настройка
echo ========================================
echo.

REM Создание .env файлов из примеров
echo [1/5] Создание конфигурационных файлов...

if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo ✓ Создан backend\.env
) else (
    echo ✓ backend\.env уже существует
)

if not exist "frontend\.env.local" (
    copy ".env.example" "frontend\.env.local"
    echo ✓ Создан frontend\.env.local
) else (
    echo ✓ frontend\.env.local уже существует
)

if not exist "steam-bot\.env" (
    echo STEAM_USERNAME=your_bot_username > "steam-bot\.env"
    echo STEAM_PASSWORD=your_bot_password >> "steam-bot\.env"
    echo STEAM_SHARED_SECRET=your_shared_secret >> "steam-bot\.env"
    echo IDENTITY_SECRET=your_identity_secret >> "steam-bot\.env"
    echo API_URL=http://localhost:8000 >> "steam-bot\.env"
    echo PORT=3001 >> "steam-bot\.env"
    echo ✓ Создан steam-bot\.env (ТРЕБУЕТСЯ НАСТРОЙКА!)
) else (
    echo ✓ steam-bot\.env уже существует
)

echo.

REM Установка зависимостей Backend
echo [2/5] Установка зависимостей Backend...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости Backend
    pause
    exit /b 1
)
echo ✓ Backend зависимости установлены
cd ..
echo.

REM Создание БД
echo [3/5] Создание базы данных...
cd backend
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось создать БД
    pause
    exit /b 1
)
echo ✓ База данных создана
cd ..
echo.

REM Установка зависимостей Steam Bot
echo [4/5] Установка зависимостей Steam Bot...
cd steam-bot
call npm install
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости Steam Bot
    pause
    exit /b 1
)
echo ✓ Steam Bot зависимости установлены
cd ..
echo.

REM Установка зависимостей Frontend
echo [5/5] Установка зависимостей Frontend...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости Frontend
    pause
    exit /b 1
)
echo ✓ Frontend зависимости установлены
cd ..
echo.

echo ========================================
echo   ✅ Настройка завершена!
echo ========================================
echo.
echo ВАЖНО: Настройте следующие файлы:
echo.
echo 1. backend\.env
echo    - STEAM_API_KEY (получите на steamcommunity.com/dev/apikey)
echo    - JWT_SECRET (случайная строка минимум 32 символа)
echo.
echo 2. steam-bot\.env
echo    - STEAM_USERNAME (логин бота)
echo    - STEAM_PASSWORD (пароль бота)
echo    - STEAM_SHARED_SECRET (из Steam Desktop Authenticator)
echo    - IDENTITY_SECRET (из Steam Desktop Authenticator)
echo.
echo 3. frontend\.env.local
echo    - Обычно не требует изменений для локальной разработки
echo.
echo После настройки запустите: start-all.bat
echo.
pause
