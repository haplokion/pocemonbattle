"""
Конфигурация приложения 'Покемон-баттл'
"""
import os

# Параметры подключения к СУБД Oracle
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SERVICE = os.getenv("ORACLE_SERVICE", "FREEPDB1")  # По умолчанию для Oracle 23c Free / XE: XEPDB1 или FREEPDB1
ORACLE_ADMIN_USER = os.getenv("ORACLE_ADMIN_USER", "SYSTEM")
ORACLE_ADMIN_PASSWORD = os.getenv("ORACLE_ADMIN_PASSWORD", "OraclePassword#123")

# Режим работы: 'auto' (пробует Oracle, при недоступности включает встроенный эмулятор для проверки логики),
# 'oracle_only' (строго требует Oracle), 'mock' (только эмуляция для автономного тестирования)
DB_MODE = os.getenv("DB_MODE", "auto")

# Порт веб-сервера
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
