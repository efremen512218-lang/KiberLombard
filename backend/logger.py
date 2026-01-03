"""
Настройка логирования для приложения
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name: str = "cyberlombard") -> logging.Logger:
    """
    Настроить логгер с выводом в файл и консоль
    
    Args:
        name: Имя логгера
        
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Избегаем дублирования handlers
    if logger.handlers:
        return logger
    
    # Создать директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler для файла (ротация по размеру)
    file_handler = RotatingFileHandler(
        log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Handler для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Handler для ошибок (отдельный файл)
    error_handler = RotatingFileHandler(
        log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    
    return logger


# Глобальный логгер
logger = setup_logger()
