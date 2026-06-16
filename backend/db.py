import os
import sqlite3
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from . import config
from .game_logic import calculate_damage, check_team_defeat

try:
    import oracledb
    ORACLEDB_AVAILABLE = True
except ImportError:
    ORACLEDB_AVAILABLE = False


class DatabaseManager:
    def __init__(self):
        self.is_oracle_active = False
        self.sqlite_conn: Optional[sqlite3.Connection] = None
        self._init_connection()

    def _init_connection(self):
        if config.DB_MODE in ("auto", "oracle_only") and ORACLEDB_AVAILABLE:
            try:
                test_conn = oracledb.connect(
                    user=config.ORACLE_ADMIN_USER,
                    password=config.ORACLE_ADMIN_PASSWORD,
                    host=config.ORACLE_HOST,
                    port=config.ORACLE_PORT,
                    service_name=config.ORACLE_SERVICE
                )
                test_conn.close()
                return
            except Exception as e:
                if config.DB_MODE == "oracle_only":
                    raise ConnectionError(f"Ошибка подключения к Oracle DB: {e}")
                print(f"[DB] Oracle DB недоступна ({e}). Включен расширенный локальный эмулятор.")

        self._init_sqlite_schema()

    def _init_sqlite_schema(self):
        db_path = os.path.join(os.path.dirname(__file__), "..", "local_game.db")
        self.sqlite_conn = sqlite3.connect(db_path, check_same_thread=False)
        self.sqlite_conn.row_factory = sqlite3.Row
        cur = self.sqlite_conn.cursor()

        cur.executescript("""
        CREATE TABLE IF NOT EXISTS ELEMENTS (
            element_id TEXT PRIMARY KEY,
            name_ru TEXT NOT NULL,
            color_hex TEXT NOT NULL,
            icon TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS ELEMENT_ADVANTAGES (
            attacker_element TEXT NOT NULL,
            defender_element TEXT NOT NULL,
            multiplier REAL DEFAULT 1.0 NOT NULL,
            PRIMARY KEY (attacker_element, defender_element)
        );

        CREATE TABLE IF NOT EXISTS CREATURE_TEMPLATES (
            template_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            element_id TEXT NOT NULL,
            base_hp INTEGER NOT NULL,
            base_attack INTEGER NOT NULL,
            base_defense INTEGER NOT NULL,
            base_speed INTEGER NOT NULL,
            sprite_name TEXT NOT NULL,
            unlock_level INTEGER DEFAULT 1 NOT NULL,
            evolution_level INTEGER DEFAULT 0 NOT NULL,
            evolves_to_id INTEGER,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS PLAYERS (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            db_username TEXT NOT NULL UNIQUE,
            password_hash TEXT DEFAULT 'demo' NOT NULL,
            display_name TEXT NOT NULL,
            level INTEGER DEFAULT 1 NOT NULL,
            exp INTEGER DEFAULT 0 NOT NULL,
            coins INTEGER DEFAULT 150 NOT NULL,
            elo_rating INTEGER DEFAULT 1000 NOT NULL,
            season_rank TEXT DEFAULT 'BRONZE' NOT NULL,
            battles_won INTEGER DEFAULT 0 NOT NULL,
            battles_lost INTEGER DEFAULT 0 NOT NULL,
            math_train_count INTEGER DEFAULT 0 NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL
        );

        CREATE TABLE IF NOT EXISTS PLAYER_CREATURES (
            creature_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            template_id INTEGER NOT NULL,
            nickname TEXT,
            level INTEGER DEFAULT 1 NOT NULL,
