@echo off
echo ========================================
echo   КиберЛомбард - Запуск всех сервисов
echo ========================================
echo.

REM Проверка .env файлов
echo [1/4] Проверка конфигурации...
if not exist "backend\.env" (
    echo ОШИБКА: Не найден backend\.env
    echo Скопируйте backend\.env.example в backend\.env и настройте
    pause
    exit /b 1
)

if not exist "steam-bot\.env" (
    echo ОШИБКА: Не найден steam-bot\.env
    echo Создайте steam-bot\.env с настройками Steam бота
    pause
    exit /b 1
)

if not exist "frontend\.env.local" (
    echo ОШИБКА: Не найден frontend\.env.local
    echo Скопируйте frontend\.env.local.example в frontend\.env.local
    pause
    exit /b 1
)

echo ✓ Конфигурация найдена
echo.

REM Запуск Backend
echo [2/4] Запуск Backend (FastAPI)...
start "КиберЛомбард Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul
echo ✓ Backend запущен на http://localhost:8000
echo.

REM Запуск Steam Bot
echo [3/4] Запуск Steam Bot...
start "КиберЛомбард Steam Bot" cmd /k "cd steam-bot && npm start"
timeout /t 3 /nobreak >nul
echo ✓ Steam Bot запущен на http://localhost:3001
echo.

REM Запуск Frontend
echo [4/4] Запуск Frontend (Next.js)...
start "КиберЛомбард Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 3 /nobreak >nul
echo ✓ Frontend запущен на http://localhost:3000
echo.

echo ========================================
echo   ✅ Все сервисы запущены!
echo ========================================
echo.
echo Backend:     http://localhost:8000
echo API Docs:    http://localhost:8000/docs
echo Steam Bot:   http://localhost:3001
echo Frontend:    http://localhost:3000
echo.
echo Для остановки закройте все окна терминалов
echo.
pause
