"""
Скрипт для создания миграции новых моделей

Запуск:
cd backend
python alembic_migration_add_models.py
"""
import subprocess
import sys

def create_migration():
    """Создать миграцию для новых моделей"""
    
    print("=" * 60)
    print("СОЗДАНИЕ МИГРАЦИИ НОВЫХ МОДЕЛЕЙ")
    print("=" * 60)
    
    print("\nНовые модели:")
    print("  - KYCVerification")
    print("  - DealSignature")
    print("  - SBPPayout")
    print("  - AuditLog (обновлена)")
    
    print("\n1. Создаём миграцию...")
    try:
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "add_kyc_signature_payout_models"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✅ Миграция создана")
            print(result.stdout)
        else:
            print("   ❌ Ошибка создания миграции")
            print(result.stderr)
            return False
    
    except FileNotFoundError:
        print("   ❌ Alembic не найден")
        print("   Установите: pip install alembic")
        return False
    
    print("\n2. Применяем миграцию...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✅ Миграция применена")
            print(result.stdout)
        else:
            print("   ❌ Ошибка применения миграции")
            print(result.stderr)
            return False
    
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ МИГРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)
    print("\nНовые таблицы созданы:")
    print("  - kyc_verifications")
    print("  - deal_signatures")
    print("  - sbp_payouts")
    print("  - audit_logs (обновлена)")
    
    return True

if __name__ == "__main__":
    success = create_migration()
    sys.exit(0 if success else 1)
