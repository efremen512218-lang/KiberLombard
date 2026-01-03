import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Тест health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_verify_steam_user():
    """Тест верификации Steam пользователя"""
    response = client.post(
        "/api/auth/steam/verify",
        params={"steam_id": "76561198000000000"}
    )
    assert response.status_code in [200, 404]  # 404 если Steam API недоступен

def test_send_phone_code():
    """Тест отправки SMS-кода"""
    response = client.post(
        "/api/kyc/phone/send-code",
        params={"phone": "+79991234567"}
    )
    assert response.status_code == 200
    assert "dev_code" in response.json()  # В dev режиме возвращается код

def test_calculate_quote():
    """Тест расчета quote"""
    response = client.post(
        "/api/quote",
        json={
            "steam_id": "76561198000000000",
            "asset_ids": ["123", "456"],
            "option_days": 14
        }
    )
    # Может быть 200 или 400 в зависимости от доступности Steam API
    assert response.status_code in [200, 400]

def test_get_inventory():
    """Тест получения инвентаря"""
    response = client.get("/api/inventory/76561198000000000")
    assert response.status_code == 200
    data = response.json()
    assert "steam_id" in data
    assert "items" in data
