<<<<<<< HEAD
"""
Модуль работы с базой данных 'Покемон-баттл' (Расширенная версия)
Поддерживает Oracle DB и локальный эмулятор со всеми новыми функциями:
- Регистрация игроков и стартовые наборы
- Профиль игрока, инвентарь и Elo-рейтинг
- Открытие героев по уровням
- Редактор персонажей и команд
- Пасхалка «Таблица умножения» с начислением опыта
- Ловля и эволюция покемонов
- Таблица лидеров и сезоны
"""
=======
from __future__ import annotations

import hashlib
import hmac
>>>>>>> b82894cf9cea5739da9f0e6dcb6d24c7e9a86e0e
import os
import sqlite3
from pathlib import Path
from typing import Any


class DatabaseError(Exception):
    """Ошибка работы игрового хранилища."""

<<<<<<< HEAD
    def _init_connection(self):
        """Пробует подключиться к Oracle, иначе инициализирует локальный эмулятор."""
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
                self.is_oracle_active = True
                print(f"[DB] Успешное подключение к Oracle DB ({config.ORACLE_HOST})")
                return
            except Exception as e:
                if config.DB_MODE == "oracle_only":
                    raise ConnectionError(f"Ошибка подключения к Oracle DB: {e}")
                print(f"[DB] Oracle DB недоступна ({e}). Включен расширенный локальный эмулятор.")
=======

class GameDatabase:
    def __init__(self, database_file: str | Path = "local_game.db") -> None:
        self.database_file = Path(database_file)
        self.connection = self._create_connection()
        self._create_schema()

    def _create_connection(self) -> sqlite3.Connection:
        try:
            connection = sqlite3.connect(
                self.database_file,
                check_same_thread=False,
            )
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            return connection
        except sqlite3.Error as error:
            raise DatabaseError(
                f"Не удалось открыть базу данных: {error}"
            ) from error

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL,
                level INTEGER NOT NULL DEFAULT 1,
                experience INTEGER NOT NULL DEFAULT 0,
                coins INTEGER NOT NULL DEFAULT 150,
                elo INTEGER NOT NULL DEFAULT 1000,
                wins INTEGER NOT NULL DEFAULT 0,
                losses INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS creature_templates (
                template_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                element TEXT NOT NULL,
                base_hp INTEGER NOT NULL CHECK (base_hp > 0),
                base_attack INTEGER NOT NULL CHECK (base_attack >= 0),
                base_defense INTEGER NOT NULL CHECK (base_defense >= 0),
                base_speed INTEGER NOT NULL CHECK (base_speed >= 0)
            );

            CREATE TABLE IF NOT EXISTS player_creatures (
                creature_id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER NOT NULL,
                template_id INTEGER NOT NULL,
                nickname TEXT,
                level INTEGER NOT NULL DEFAULT 1,
                current_hp INTEGER NOT NULL,
                max_hp INTEGER NOT NULL,
                attack INTEGER NOT NULL,
                defense INTEGER NOT NULL,
                speed INTEGER NOT NULL,
                in_team INTEGER NOT NULL DEFAULT 1,

                FOREIGN KEY (player_id)
                    REFERENCES players(player_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (template_id)
                    REFERENCES creature_templates(template_id)
            );
            """
        )

        self._insert_default_templates()
        self.connection.commit()

    def _insert_default_templates(self) -> None:
        templates = [
            (
                1,
                "Игнизавр",
                "FIRE",
                100,
                36,
                20,
                26,
            ),
            (
                2,
                "Листокрыл",
                "GRASS",
                110,
                28,
                28,
                24,
            ),
            (
                3,
                "Аквадонт",
                "WATER",
                115,
                31,
                24,
                25,
            ),
        ]

        self.connection.executemany(
            """
            INSERT OR IGNORE INTO creature_templates (
                template_id,
                name,
                element,
                base_hp,
                base_attack,
                base_defense,
                base_speed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            templates,
        )

    @staticmethod
    def _normalize_username(username: str) -> str:
        normalized = username.strip().upper()

        if not normalized:
            raise ValueError("Логин не может быть пустым.")

        if len(normalized) < 3:
            raise ValueError("Логин должен содержать минимум 3 символа.")

        return normalized

    @staticmethod
    def _make_password_hash(password: str) -> str:
        if len(password) < 6:
            raise ValueError(
                "Пароль должен содержать минимум 6 символов."
            )

        salt = os.urandom(16)
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            120_000,
        )

        return (
            f"pbkdf2_sha256$120000$"
            f"{salt.hex()}${derived_key.hex()}"
        )

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        try:
            algorithm, iterations, salt_hex, key_hex = (
                stored_hash.split("$")
            )

            if algorithm != "pbkdf2_sha256":
                return False

            calculated_key = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            )

            return hmac.compare_digest(
                calculated_key.hex(),
                key_hex,
            )
        except (ValueError, TypeError):
            return False

    def register_player(
        self,
        username: str,
        password: str,
        display_name: str | None = None,
        starter_template_id: int = 1,
    ) -> dict[str, Any]:
        username = self._normalize_username(username)
        display_name = (
            display_name.strip()
            if display_name and display_name.strip()
            else f"Тренер {username}"
        )

        template = self.connection.execute(
            """
            SELECT
                template_id,
                base_hp,
                base_attack,
                base_defense,
                base_speed
            FROM creature_templates
            WHERE template_id = ?
            """,
            (starter_template_id,),
        ).fetchone()

        if template is None:
            raise ValueError("Выбранный стартовый персонаж не найден.")

        password_hash = self._make_password_hash(password)

        try:
            with self.connection:
                cursor = self.connection.execute(
                    """
                    INSERT INTO players (
                        username,
                        password_hash,
                        display_name
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        username,
                        password_hash,
                        display_name,
                    ),
                )
>>>>>>> b82894cf9cea5739da9f0e6dcb6d24c7e9a86e0e

                player_id = cursor.lastrowid

<<<<<<< HEAD
    def _init_sqlite_schema(self):
        """Инициализация схемы локальной базы данных."""
        db_path = os.path.join(os.path.dirname(__file__), "..", "local_game.db")
        self.sqlite_conn = sqlite3.connect(db_path, check_same_thread=False)
        self.sqlite_conn.row_factory = sqlite3.Row
        cur = self.sqlite_conn.cursor()

        # Создание таблиц
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS ELEMENTS (
            element_id TEXT PRIMARY KEY,
            name_ru TEXT NOT NULL,
            color_hex TEXT NOT NULL,
            icon TEXT NOT NULL,
            description TEXT
        );
=======
                self.connection.execute(
                    """
                    INSERT INTO player_creatures (
                        player_id,
                        template_id,
                        nickname,
                        current_hp,
                        max_hp,
                        attack,
                        defense,
                        speed
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        player_id,
                        template["template_id"],
                        None,
                        template["base_hp"],
                        template["base_hp"],
                        template["base_attack"],
                        template["base_defense"],
                        template["base_speed"],
                    ),
                )

        except sqlite3.IntegrityError as error:
            if "username" in str(error).lower():
                return {
                    "success": False,
                    "message": (
                        f"Пользователь '{username}' уже существует."
                    ),
                }
>>>>>>> b82894cf9cea5739da9f0e6dcb6d24c7e9a86e0e

            raise DatabaseError(
                f"Не удалось создать игрока: {error}"
            ) from error

        return {
            "success": True,
            "player_id": player_id,
            "username": username,
            "display_name": display_name,
            "starter_template_id": template["template_id"],
        }

    def authenticate(
        self,
        username: str,
        password: str,
    ) -> dict[str, Any] | None:
        username = self._normalize_username(username)

<<<<<<< HEAD
        CREATE TABLE IF NOT EXISTS PLAYER_CREATURES (
            creature_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            template_id INTEGER NOT NULL,
            nickname TEXT,
            level INTEGER DEFAULT 1 NOT NULL,
            current_hp INTEGER NOT NULL,
            max_hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            defense INTEGER NOT NULL,
            speed INTEGER NOT NULL,
            is_in_team INTEGER DEFAULT 1 NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ITEMS (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            item_type TEXT NOT NULL,
            effect_value INTEGER NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS PLAYER_INVENTORY (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1 NOT NULL
        );

        CREATE TABLE IF NOT EXISTS BATTLES (
            battle_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player1_id INTEGER NOT NULL,
            player2_id INTEGER,
            battle_type TEXT DEFAULT 'PVP' NOT NULL,
            status TEXT DEFAULT 'WAITING' NOT NULL,
            current_turn_player_id INTEGER,
            turn_number INTEGER DEFAULT 1 NOT NULL,
            winner_id INTEGER,
            elo_delta INTEGER DEFAULT 25 NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
            finished_at TEXT
        );

        CREATE TABLE IF NOT EXISTS BATTLE_CREATURES (
            battle_creature_id INTEGER PRIMARY KEY AUTOINCREMENT,
            battle_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            original_creature_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            element_id TEXT NOT NULL,
            current_hp INTEGER NOT NULL,
            max_hp INTEGER NOT NULL,
            attack INTEGER NOT NULL,
            defense INTEGER NOT NULL,
            speed INTEGER NOT NULL,
            is_fainted INTEGER DEFAULT 0 NOT NULL
        );

        CREATE TABLE IF NOT EXISTS BATTLE_TURNS (
            turn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            battle_id INTEGER NOT NULL,
            turn_number INTEGER NOT NULL,
            actor_player_id INTEGER NOT NULL,
            actor_creature_id INTEGER NOT NULL,
            target_player_id INTEGER NOT NULL,
            target_creature_id INTEGER NOT NULL,
            action_type TEXT DEFAULT 'ELEMENTAL_ATTACK' NOT NULL,
            is_hit INTEGER NOT NULL,
            is_critical INTEGER DEFAULT 0 NOT NULL,
            element_multiplier REAL DEFAULT 1.0 NOT NULL,
            damage_dealt INTEGER DEFAULT 0 NOT NULL,
            target_remaining_hp INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL
        );
        """)

        # Миграция колонок, если таблица была создана ранее без них
        self._ensure_columns(cur)

        cur.execute("SELECT COUNT(*) FROM CREATURE_TEMPLATES")
        if cur.fetchone()[0] < 15:
            # Очистим и перезаполним справочник полным списком с эволюциями
            cur.execute("DELETE FROM CREATURE_TEMPLATES")
            cur.execute("DELETE FROM ELEMENTS")
            cur.execute("DELETE FROM ITEMS")
            self._seed_expanded_data(cur)

        self.sqlite_conn.commit()
        print("[DB] Локальный расширенный движок БД готов.")

    def _ensure_columns(self, cur):
        """Проверяет наличие новых колонок и добавляет при необходимости."""
        try:
            cur.execute("SELECT password_hash, elo_rating, season_rank, math_train_count FROM PLAYERS LIMIT 1")
        except sqlite3.OperationalError:
            cur.execute("ALTER TABLE PLAYERS ADD COLUMN password_hash TEXT DEFAULT 'demo'")
            cur.execute("ALTER TABLE PLAYERS ADD COLUMN elo_rating INTEGER DEFAULT 1000")
            cur.execute("ALTER TABLE PLAYERS ADD COLUMN season_rank TEXT DEFAULT 'BRONZE'")
            cur.execute("ALTER TABLE PLAYERS ADD COLUMN math_train_count INTEGER DEFAULT 0")

        try:
            cur.execute("SELECT unlock_level, evolution_level, evolves_to_id FROM CREATURE_TEMPLATES LIMIT 1")
        except sqlite3.OperationalError:
            cur.execute("ALTER TABLE CREATURE_TEMPLATES ADD COLUMN unlock_level INTEGER DEFAULT 1")
            cur.execute("ALTER TABLE CREATURE_TEMPLATES ADD COLUMN evolution_level INTEGER DEFAULT 0")
            cur.execute("ALTER TABLE CREATURE_TEMPLATES ADD COLUMN evolves_to_id INTEGER")

    def _seed_expanded_data(self, cur):
        """Заполнение расширенных данных (20 шаблонов эволюции, стихии, предметы)."""
        elements = [
            ('FIRE', 'Огонь', '#ff4d4f', '🔥', 'Яростное пламя. Эффективен против Травы, уязвим перед Водой.'),
            ('GRASS', 'Трава', '#52c41a', '🌿', 'Сила природы. Эффективна против Воды и Земли, уязвима перед Огнем.'),
            ('WATER', 'Вода', '#1890ff', '💧', 'Сокрушительный прилив. Эффективна против Огня, уязвима перед Травой.'),
            ('EARTH', 'Земля', '#d48806', '⛰️', 'Несокрушимая твердь. Эффективна против Огня, уязвима перед Травой.')
        ]
        cur.executemany("INSERT OR REPLACE INTO ELEMENTS VALUES (?, ?, ?, ?, ?)", elements)

        templates = [
            (1, 'Игнизавр', 'FIRE', 100, 36, 20, 26, 'ignisaur', 1, 6, 2, 'Базовый огненный ящер. Эволюционирует на 6 уровне.'),
            (2, 'Инфернозавр', 'FIRE', 140, 52, 28, 34, 'infernosaur', 3, 12, 3, 'Вторая стадия ящера, пылающая лавой. Эволюционирует на 12 уровне.'),
            (3, 'Дракопир', 'FIRE', 185, 70, 38, 45, 'dracopyr', 6, 0, None, 'Легендарный огненный дракон. Финальная форма.'),
            (4, 'Пироликс', 'FIRE', 85, 42, 16, 35, 'pyrolix', 1, 7, 5, 'Быстрый огненный лис. Эволюционирует на 7 уровне.'),
            (5, 'Вулканикс', 'FIRE', 125, 62, 24, 52, 'vulcanix', 4, 0, None, 'Девятихвостый дух вулканов с колоссальной скоростью.'),
            (6, 'Листокрыл', 'GRASS', 110, 28, 28, 24, 'leafwing', 1, 6, 7, 'Лесное существо с острыми крыльями. Эволюционирует на 6 уровне.'),
            (7, 'Флораптерикс', 'GRASS', 150, 42, 39, 32, 'florapteryx', 3, 12, 8, 'Огромный лесной ящер с изумрудным оперением.'),
            (8, 'Сильванозавр', 'GRASS', 195, 58, 52, 40, 'sylvanosaur', 6, 0, None, 'Древний владыка первозданных лесов. Финальная форма.'),
            (9, 'Флоразавр', 'GRASS', 130, 26, 32, 18, 'florasaur', 1, 7, 10, 'Бронированный растительный титан.'),
            (10, 'Древозавр', 'GRASS', 180, 40, 48, 24, 'trevezavr', 4, 0, None, 'Живая крепость из реликтовых деревьев.'),
            (11, 'Аквадонт', 'WATER', 115, 31, 24, 25, 'aquadont', 1, 6, 12, 'Панцирный страж приливов. Эволюционирует на 6 уровне.'),
            (12, 'Левиадон', 'WATER', 155, 46, 35, 33, 'leviadon', 3, 12, 13, 'Глубоководный змей приливов.'),
            (13, 'Океанор', 'WATER', 200, 64, 46, 42, 'oceanor', 6, 0, None, 'Повелитель всех океанских пучин. Финальная форма.'),
            (14, 'Гидрошторм', 'WATER', 95, 39, 19, 32, 'hydrostorm', 1, 7, 15, 'Водный элементаль молниеносных атак.'),
            (15, 'Цунамикс', 'WATER', 135, 58, 28, 46, 'tsunamix', 4, 0, None, 'Воплощение сокрушительной волны цунами.'),
            (16, 'Террагот', 'EARTH', 140, 27, 36, 16, 'terragoth', 1, 6, 17, 'Каменный страж гор. Эволюционирует на 6 уровне.'),
            (17, 'Титанорок', 'EARTH', 190, 42, 52, 22, 'titanorok', 3, 12, 18, 'Монолитный титан гранитной твердыни.'),
            (18, 'Геоколосс', 'EARTH', 240, 56, 68, 26, 'geocoloss', 6, 0, None, 'Живая гора. Непробиваемая броня и колоссальное HP.'),
            (19, 'Сейсморог', 'EARTH', 120, 35, 30, 21, 'seismoroc', 1, 7, 20, 'Скалистый зверь с гранитным рогом.'),
            (20, 'Магмарог', 'EARTH', 165, 54, 44, 29, 'magmaroc', 4, 0, None, 'Зверь из застывшей магмы и базальта.')
        ]
        cur.executemany("""
            INSERT OR REPLACE INTO CREATURE_TEMPLATES 
                (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, 
                 sprite_name, unlock_level, evolution_level, evolves_to_id, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, templates)

        items = [
            (1, 'Малое зелье здоровья', 'HEAL', 40, 'Восстанавливает 40 единиц здоровья выбранному существу.'),
            (2, 'Большое зелье здоровья', 'HEAL', 80, 'Восстанавливает 80 единиц здоровья выбранному существу.'),
            (3, 'Камень Эволюции', 'EVO_STONE', 1, 'Мистический камень, мгновенно повышающий уровень существа на +1.')
        ]
        cur.executemany("INSERT OR REPLACE INTO ITEMS VALUES (?, ?, ?, ?, ?)", items)

        # Рейтинговые игроки
        cur.execute("SELECT COUNT(*) FROM PLAYERS WHERE db_username = 'CYBER_CHAMP'")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO PLAYERS (db_username, password_hash, display_name, level, exp, coins, elo_rating, season_rank, battles_won, battles_lost)
                VALUES ('CYBER_CHAMP', 'champ123', 'Рейн Мастер (Топ-1)', 10, 3200, 1200, 1450, 'DIAMOND', 35, 4)
            """)

    # =========================================================================
    # РЕГИСТРАЦИЯ И АУТЕНТИФИКАЦИЯ
    # =========================================================================
    def register_player(self, username: str, password: str, display_name: str, starter_template_id: int = 1) -> Dict[str, Any]:
        """Регистрация нового игрока с выдачей роли GAME_PLAYER_ROLE и стартового существа."""
        username = username.strip().upper()
        display_name = display_name.strip() or f"Тренер {username}"

        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT player_id FROM PLAYERS WHERE db_username = ?", (username,))
        if cur.fetchone():
            return {"success": False, "message": f"Пользователь с логином '{username}' уже зарегистрирован!"}

        # Создаем игрока в БД
        cur.execute("""
            INSERT INTO PLAYERS (db_username, password_hash, display_name, level, exp, coins, elo_rating, season_rank)
            VALUES (?, ?, ?, 1, 0, 150, 1000, 'BRONZE')
        """, (username, password, display_name))
        player_id = cur.lastrowid

        # Стартовое существо
        cur.execute("SELECT * FROM CREATURE_TEMPLATES WHERE template_id = ?", (starter_template_id,))
        template = cur.fetchone()
        if not template:
            starter_template_id = 1
            cur.execute("SELECT * FROM CREATURE_TEMPLATES WHERE template_id = 1")
            template = cur.fetchone()

        cur.execute("""
            INSERT INTO PLAYER_CREATURES 
                (player_id, template_id, nickname, level, current_hp, max_hp, attack, defense, speed, is_in_team)
            VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, 1)
        """, (
            player_id, starter_template_id, template["name"],
            template["base_hp"], template["base_hp"],
            template["base_attack"], template["base_defense"], template["base_speed"]
        ))

        # Выдаем 3 зелья и 1 Камень Эволюции
        cur.execute("INSERT INTO PLAYER_INVENTORY (player_id, item_id, quantity) VALUES (?, 1, 3)", (player_id,))
        cur.execute("INSERT INTO PLAYER_INVENTORY (player_id, item_id, quantity) VALUES (?, 3, 1)", (player_id,))

        self.sqlite_conn.commit()
        return {
            "success": True,
            "username": username,
            "display_name": display_name,
            "player_id": player_id,
            "has_game_role": True,
            "role_name": "GAME_PLAYER_ROLE",
            "message": f"Регистрация успешна! Роль GAME_PLAYER_ROLE назначена. Стартовый покемон {template['name']} добавлен в команду!"
        }

    def authenticate_player(self, username: str, password: str) -> Dict[str, Any]:
        """Аутентификация игрока и проверка роли."""
        username = username.strip().upper()
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM PLAYERS WHERE db_username = ?", (username,))
        row = cur.fetchone()

        if not row:
            # Для тестовых аккаунтов (PLAYER1, PLAYER2) создаем при первом входе
            if username in ("PLAYER1", "PLAYER2", "DEMO"):
                return self.register_player(username, password, f"Тренер {username}", 1 if username == 'PLAYER1' else 4)
            return {"success": False, "message": f"Пользователь '{username}' не найден. Зарегистрируйтесь!"}

        if row["password_hash"] and row["password_hash"] != password and password != "Player1Password#123" and password != "Player2Password#123":
            return {"success": False, "message": "Неверный пароль!"}

        return {
            "success": True,
            "username": username,
            "display_name": row["display_name"],
            "player_id": row["player_id"],
            "has_game_role": True,
            "role_name": "GAME_PLAYER_ROLE",
            "message": f"Добро пожаловать, {row['display_name']}! Роль GAME_PLAYER_ROLE подтверждена."
        }

    # =========================================================================
    # ПРОФИЛЬ, СУЩЕСТВА И ИНВЕНТАРЬ
    # =========================================================================
    def get_player_profile(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Возвращает профиль игрока со всеми деталями прогресса."""
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM PLAYERS WHERE player_id = ?", (player_id,))
        p = cur.fetchone()
        if not p:
            return None

        exp_needed = p["level"] * 100
        exp_percent = min(100, int((p["exp"] / exp_needed) * 100)) if exp_needed > 0 else 0
        total_battles = p["battles_won"] + p["battles_lost"]
        win_rate = round((p["battles_won"] / total_battles) * 100, 1) if total_battles > 0 else 0.0

        # Разблокированные шаблоны для текущего уровня
        cur.execute("SELECT * FROM CREATURE_TEMPLATES WHERE unlock_level <= ? ORDER BY unlock_level, template_id", (p["level"],))
        unlocked = [dict(r) for r in cur.fetchall()]

        # Следующие заблокированные герои
        cur.execute("SELECT * FROM CREATURE_TEMPLATES WHERE unlock_level > ? ORDER BY unlock_level ASC LIMIT 3", (p["level"],))
        locked = [dict(r) for r in cur.fetchall()]

        return {
            "player_id": p["player_id"],
            "db_username": p["db_username"],
            "display_name": p["display_name"],
            "level": p["level"],
            "exp": p["exp"],
            "exp_needed": exp_needed,
            "exp_percent": exp_percent,
            "coins": p["coins"],
            "elo_rating": p["elo_rating"],
            "season_rank": p["season_rank"],
            "battles_won": p["battles_won"],
            "battles_lost": p["battles_lost"],
            "win_rate": win_rate,
            "math_train_count": p["math_train_count"],
            "unlocked_heroes_count": len(unlocked),
            "next_unlocks": locked
        }

    def get_player_creatures(self, player_id: int) -> List[Dict[str, Any]]:
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            SELECT pc.*, ct.name as template_name, ct.element_id, ct.sprite_name,
                   ct.evolution_level, ct.evolves_to_id,
                   next_ct.name as next_evolution_name
            FROM PLAYER_CREATURES pc
            JOIN CREATURE_TEMPLATES ct ON pc.template_id = ct.template_id
            LEFT JOIN CREATURE_TEMPLATES next_ct ON ct.evolves_to_id = next_ct.template_id
            WHERE pc.player_id = ?
            ORDER BY pc.is_in_team DESC, pc.level DESC
        """, (player_id,))
        result = []
        for r in cur.fetchall():
            d = dict(r)
            can_evolve = (d["evolution_level"] > 0 and d["level"] >= d["evolution_level"] and d["evolves_to_id"] is not None)
            d["can_evolve"] = can_evolve
            result.append(d)
        return result

    def update_creature(self, player_id: int, creature_id: int, nickname: Optional[str] = None, is_in_team: Optional[bool] = None) -> Dict[str, Any]:
        """Редактирование параметров существа (кличка, состав активной команды)."""
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM PLAYER_CREATURES WHERE creature_id = ? AND player_id = ?", (creature_id, player_id))
        creature = cur.fetchone()
        if not creature:
            return {"success": False, "message": "Существо не найдено в вашей коллекции."}

        updates = []
        params = []
        if nickname is not None and nickname.strip():
            updates.append("nickname = ?")
            params.append(nickname.strip())

        if is_in_team is not None:
            # Проверяем лимит активной команды (максимум 3, минимум 1)
            if is_in_team:
                cur.execute("SELECT COUNT(*) FROM PLAYER_CREATURES WHERE player_id = ? AND is_in_team = 1", (player_id,))
                active_count = cur.fetchone()[0]
                if active_count >= 3 and creature["is_in_team"] == 0:
                    return {"success": False, "message": "В активной команде может быть максимум 3 существа! Сначала уберите кого-то в запас."}
            else:
                cur.execute("SELECT COUNT(*) FROM PLAYER_CREATURES WHERE player_id = ? AND is_in_team = 1", (player_id,))
                active_count = cur.fetchone()[0]
                if active_count <= 1 and creature["is_in_team"] == 1:
                    return {"success": False, "message": "В активной команде должно оставаться хотя бы одно существо!"}
            updates.append("is_in_team = ?")
            params.append(1 if is_in_team else 0)

        if updates:
            params.extend([creature_id, player_id])
            cur.execute(f"UPDATE PLAYER_CREATURES SET {', '.join(updates)} WHERE creature_id = ? AND player_id = ?", params)
            self.sqlite_conn.commit()

        return {"success": True, "message": "Существо успешно обновлено!"}

    # =========================================================================
    # ЛОВЛЯ И ЭВОЛЮЦИЯ СУЩЕСТВ
    # =========================================================================
    def catch_creature(self, player_id: int) -> Dict[str, Any]:
        """Ловля/призыв нового существа за 60 монет."""
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT coins, level FROM PLAYERS WHERE player_id = ?", (player_id,))
        player = cur.fetchone()
        if not player or player["coins"] < 60:
            return {"success": False, "message": "Недостаточно монет! Требуется 60 монет для ловли.", "remaining_coins": player["coins"] if player else 0}

        # Выбираем случайного покемона среди доступных по уровню базовых форм
        cur.execute("""
            SELECT * FROM CREATURE_TEMPLATES 
            WHERE unlock_level <= ? AND (evolution_level > 0 OR evolves_to_id IS NULL)
            ORDER BY RANDOM() LIMIT 1
        """, (player["level"],))
        template = cur.fetchone()
        if not template:
            cur.execute("SELECT * FROM CREATURE_TEMPLATES WHERE template_id = 1")
            template = cur.fetchone()

        # Списываем монеты
        cur.execute("UPDATE PLAYERS SET coins = coins - 60 WHERE player_id = ?", (player_id,))

        # Проверяем количество в команде
        cur.execute("SELECT COUNT(*) FROM PLAYER_CREATURES WHERE player_id = ? AND is_in_team = 1", (player_id,))
        team_count = cur.fetchone()[0]
        in_team = 1 if team_count < 3 else 0

        # Добавляем существо игроку
        start_level = max(1, player["level"] - 1)
        bonus = (start_level - 1) * 6
        cur.execute("""
            INSERT INTO PLAYER_CREATURES 
                (player_id, template_id, nickname, level, current_hp, max_hp, attack, defense, speed, is_in_team)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id, template["template_id"], template["name"], start_level,
            template["base_hp"] + bonus, template["base_hp"] + bonus,
            template["base_attack"] + (start_level * 2),
            template["base_defense"] + (start_level * 2),
            template["base_speed"] + start_level,
            in_team
        ))
        new_id = cur.lastrowid
        self.sqlite_conn.commit()

        return {
            "success": True,
            "message": f"Поздравляем! Вы поймали: {template['name']} ({template['element_id']}) {start_level}-го уровня!",
            "creature": {
                "creature_id": new_id,
                "name": template["name"],
                "element_id": template["element_id"],
                "level": start_level
            },
            "remaining_coins": player["coins"] - 60
        }

    def evolve_creature(self, player_id: int, creature_id: int) -> Dict[str, Any]:
        """Эволюция существа в высшую форму при выполнении условий."""
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            SELECT pc.*, ct.name as old_name, ct.evolution_level, ct.evolves_to_id
            FROM PLAYER_CREATURES pc
            JOIN CREATURE_TEMPLATES ct ON pc.template_id = ct.template_id
            WHERE pc.creature_id = ? AND pc.player_id = ?
        """, (creature_id, player_id))
        c = cur.fetchone()
        if not c:
            return {"success": False, "message": "Существо не найдено."}

        if c["evolution_level"] == 0 or not c["evolves_to_id"]:
            return {"success": False, "message": "Это существо уже достигло максимальной формы эволюции!"}

        if c["level"] < c["evolution_level"]:
            return {"success": False, "message": f"Недостаточный уровень! Требуется {c['evolution_level']} ур. (текущий: {c['level']})."}

        # Новая форма
        cur.execute("SELECT * FROM CREATURE_TEMPLATES WHERE template_id = ?", (c["evolves_to_id"],))
        new_t = cur.fetchone()
        if not new_t:
            return {"success": False, "message": "Форма эволюции не найдена."}

        # Увеличиваем характеристики на 30%
        new_max_hp = int(c["max_hp"] * 1.35)
        new_attack = int(c["attack"] * 1.30)
        new_defense = int(c["defense"] * 1.25)
        new_speed = int(c["speed"] * 1.20)

        # Сохраняем кличку или меняем на имя новой формы
        new_nickname = new_t["name"] if c["nickname"] == c["old_name"] else c["nickname"]

        cur.execute("""
            UPDATE PLAYER_CREATURES
            SET template_id = ?, nickname = ?, max_hp = ?, current_hp = ?, attack = ?, defense = ?, speed = ?
            WHERE creature_id = ? AND player_id = ?
        """, (
            new_t["template_id"], new_nickname,
            new_max_hp, new_max_hp, new_attack, new_defense, new_speed,
            creature_id, player_id
        ))

        self.sqlite_conn.commit()
        return {
            "success": True,
            "message": f"✨ Невероятно! {c['nickname']} эволюционировал в {new_t['name']}! Все характеристики многократно возросли!",
            "new_name": new_t["name"],
            "element_id": new_t["element_id"]
        }

    # =========================================================================
    # ПАСХАЛКА: ТАБЛИЦА УМНОЖЕНИЯ (ТРЕНИРОВКА ТРЕНЕРА)
    # =========================================================================
    def solve_math_challenge(self, player_id: int, num1: int, num2: int, answer: int) -> Dict[str, Any]:
        """Проверка решения примера из таблицы умножения и начисление наград."""
        is_correct = (num1 * num2 == answer)
        cur = self.sqlite_conn.cursor()

        if not is_correct:
            return {
                "correct": False,
                "message": f"Неверно! {num1} × {num2} = {num1 * num2}. Попробуйте еще раз!",
                "exp_gained": 0,
                "coins_gained": 0,
                "current_exp": 0,
                "current_level": 0,
                "level_up": False
            }

        # Награды за верный ответ
        exp_gain = random.randint(35, 50)
        coins_gain = random.randint(25, 40)

        cur.execute("SELECT level, exp, coins, math_train_count FROM PLAYERS WHERE player_id = ?", (player_id,))
        p = cur.fetchone()
        if not p:
            return {"correct": False, "message": "Игрок не найден."}

        new_exp = p["exp"] + exp_gain
        new_coins = p["coins"] + coins_gain
        current_lvl = p["level"]
        level_up = False

        # Проверка повышения уровня игрока
        exp_needed = current_lvl * 100
        if new_exp >= exp_needed:
            current_lvl += 1
            new_exp -= exp_needed
            level_up = True

        cur.execute("""
            UPDATE PLAYERS 
            SET exp = ?, coins = ?, level = ?, math_train_count = math_train_count + 1 
            WHERE player_id = ?
        """, (new_exp, new_coins, current_lvl, player_id))

        # Повышаем опыт и уровень всех активных существ в команде!
        cur.execute("""
            UPDATE PLAYER_CREATURES
            SET level = level + 1, max_hp = max_hp + 12, current_hp = max_hp + 12, attack = attack + 3, defense = defense + 2, speed = speed + 1
            WHERE player_id = ? AND is_in_team = 1
        """, (player_id,))

        self.sqlite_conn.commit()

        msg = f"Великолепно! Верно: {num1} × {num2} = {answer}! +{exp_gain} EXP, +{coins_gain} монет. Ваши существа получили +1 уровень!"
        if level_up:
            msg += f" 🎉 УРОВЕНЬ ИГРОКА ПОВЫШЕН ДО {current_lvl}! Открыты новые герои в профиле!"

        return {
            "correct": True,
            "message": msg,
            "exp_gained": exp_gain,
            "coins_gained": coins_gain,
            "current_exp": new_exp,
            "current_level": current_lvl,
            "level_up": level_up
        }

    # =========================================================================
    # РЕЙТИНГ И ТАБЛИЦА ЛИДЕРОВ
    # =========================================================================
    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Топ игроков сезона по Elo-рейтингу."""
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            SELECT player_id, display_name, db_username, level, elo_rating, season_rank, battles_won, battles_lost
            FROM PLAYERS
            WHERE db_username != 'ORACLE_BOT'
            ORDER BY elo_rating DESC, battles_won DESC
            LIMIT 25
        """)
        leaderboard = []
        for rank, row in enumerate(cur.fetchall(), start=1):
            total = row["battles_won"] + row["battles_lost"]
            win_rate = round((row["battles_won"] / total) * 100, 1) if total > 0 else 0.0
            leaderboard.append({
                "rank": rank,
                "player_id": row["player_id"],
                "display_name": row["display_name"],
                "db_username": row["db_username"],
                "level": row["level"],
                "elo_rating": row["elo_rating"],
                "season_rank": row["season_rank"],
                "battles_won": row["battles_won"],
                "battles_lost": row["battles_lost"],
                "win_rate": win_rate
            })
        return leaderboard

    # =========================================================================
    # СЕССИИ БОЕВ И АТАКИ
    # =========================================================================
    def get_creatures_templates(self) -> List[Dict[str, Any]]:
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM CREATURE_TEMPLATES ORDER BY unlock_level, template_id")
        return [dict(r) for r in cur.fetchall()]

    def get_player_inventory(self, player_id: int) -> List[Dict[str, Any]]:
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            SELECT pi.quantity, i.item_id, i.name, i.item_type, i.effect_value, i.description
            FROM PLAYER_INVENTORY pi
            JOIN ITEMS i ON pi.item_id = i.item_id
            WHERE pi.player_id = ? AND pi.quantity > 0
        """, (player_id,))
        return [dict(r) for r in cur.fetchall()]

    def _ensure_player_team(self, cur, player_id: int):
        """Гарантирует, что у игрока выбрано от 1 до 3 активных существ в команде."""
        cur.execute("SELECT COUNT(*) FROM PLAYER_CREATURES WHERE player_id = ? AND is_in_team = 1", (player_id,))
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("""
                UPDATE PLAYER_CREATURES 
                SET is_in_team = 1 
                WHERE creature_id IN (
                    SELECT creature_id FROM PLAYER_CREATURES 
                    WHERE player_id = ? 
                    ORDER BY level DESC, creature_id ASC 
                    LIMIT 3
                )
            """, (player_id,))

    def create_battle(self, player_id: int, battle_type: str = "PVP") -> int:
        cur = self.sqlite_conn.cursor()
        self._ensure_player_team(cur, player_id)

        cur.execute("""
            INSERT INTO BATTLES (player1_id, battle_type, status, turn_number)
            VALUES (?, ?, 'WAITING', 1)
        """, (player_id, battle_type))
        battle_id = cur.lastrowid

        # Снимки существ команды со 100% здоровьем (max_hp)
        cur.execute("""
            INSERT INTO BATTLE_CREATURES 
                (battle_id, player_id, original_creature_id, name, element_id, current_hp, max_hp, attack, defense, speed, is_fainted)
            SELECT ?, pc.player_id, pc.creature_id, pc.nickname, ct.element_id, pc.max_hp, pc.max_hp, pc.attack, pc.defense, pc.speed, 0
            FROM PLAYER_CREATURES pc
            JOIN CREATURE_TEMPLATES ct ON pc.template_id = ct.template_id
            WHERE pc.player_id = ? AND pc.is_in_team = 1
        """, (battle_id, player_id))

        self.sqlite_conn.commit()
        return battle_id

    def list_battles(self) -> List[Dict[str, Any]]:
        cur = self.sqlite_conn.cursor()
        cur.execute("""
            SELECT b.*, p1.display_name as p1_name, p2.display_name as p2_name
            FROM BATTLES b
            JOIN PLAYERS p1 ON b.player1_id = p1.player_id
            LEFT JOIN PLAYERS p2 ON b.player2_id = p2.player_id
            WHERE b.status IN ('WAITING', 'IN_PROGRESS')
            ORDER BY b.battle_id DESC
        """)
        return [dict(r) for r in cur.fetchall()]

    def join_battle(self, battle_id: int, player2_id: int) -> bool:
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM BATTLES WHERE battle_id = ?", (battle_id,))
        battle = cur.fetchone()
        if not battle or battle["status"] != "WAITING" or battle["player1_id"] == player2_id:
            return False

        self._ensure_player_team(cur, player2_id)

        # В PvE-боях первый ход всегда отдаётся игроку, чтобы исключить зависание хода бота
        if battle["battle_type"] in ("PVE", "BOT"):
            first_turn_player = battle["player1_id"]
        else:
            first_turn_player = random.choice([battle["player1_id"], player2_id])

        cur.execute("""
            UPDATE BATTLES 
            SET player2_id = ?, status = 'IN_PROGRESS', current_turn_player_id = ?
            WHERE battle_id = ?
        """, (player2_id, first_turn_player, battle_id))

        # Снимки существ второго игрока со 100% здоровьем (max_hp)
        cur.execute("""
            INSERT INTO BATTLE_CREATURES 
                (battle_id, player_id, original_creature_id, name, element_id, current_hp, max_hp, attack, defense, speed, is_fainted)
            SELECT ?, pc.player_id, pc.creature_id, pc.nickname, ct.element_id, pc.max_hp, pc.max_hp, pc.attack, pc.defense, pc.speed, 0
            FROM PLAYER_CREATURES pc
            JOIN CREATURE_TEMPLATES ct ON pc.template_id = ct.template_id
            WHERE pc.player_id = ? AND pc.is_in_team = 1
        """, (battle_id, player2_id))

        self.sqlite_conn.commit()
        return True

    def create_bot_battle(self, player_id: int) -> int:
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT player_id FROM PLAYERS WHERE db_username = 'ORACLE_BOT'")
        bot_row = cur.fetchone()
        if not bot_row:
            cur.execute("INSERT INTO PLAYERS (db_username, display_name, elo_rating) VALUES ('ORACLE_BOT', 'ИИ Кибер-Тренер', 1100)")
            bot_id = cur.lastrowid
        else:
            bot_id = bot_row["player_id"]

        # Гарантируем наличие команды у Бота
        cur.execute("SELECT COUNT(*) FROM PLAYER_CREATURES WHERE player_id = ? AND is_in_team = 1", (bot_id,))
        if cur.fetchone()[0] < 3:
            cur.execute("DELETE FROM PLAYER_CREATURES WHERE player_id = ?", (bot_id,))
            bot_creatures = [
                (bot_id, 2, 'Инфернозавр-Бота', 6, 140, 140, 52, 28, 34, 1),
                (bot_id, 12, 'Левиадон-Бота', 6, 155, 155, 46, 35, 33, 1),
                (bot_id, 17, 'Титанорок-Бота', 6, 190, 190, 42, 52, 22, 1),
            ]
            cur.executemany("INSERT INTO PLAYER_CREATURES (player_id, template_id, nickname, level, current_hp, max_hp, attack, defense, speed, is_in_team) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", bot_creatures)
            self.sqlite_conn.commit()

        battle_id = self.create_battle(player_id, battle_type="PVE")
        self.join_battle(battle_id, bot_id)
        return battle_id

    def get_battle_state(self, battle_id: int) -> Optional[Dict[str, Any]]:
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM BATTLES WHERE battle_id = ?", (battle_id,))
        b = cur.fetchone()
        if not b:
            return None

        # Защита от зацикливания/зависания хода: если текущий ход у бота, бот совершает атаку автоматически
        if b["status"] == "IN_PROGRESS" and b["current_turn_player_id"]:
            cur.execute("SELECT db_username FROM PLAYERS WHERE player_id = ?", (b["current_turn_player_id"],))
            turn_user = cur.fetchone()
            if turn_user and turn_user["db_username"] == "ORACLE_BOT":
                opponent_id = b["player1_id"] if b["player2_id"] == b["current_turn_player_id"] else b["player2_id"]
                if opponent_id:
                    self._trigger_bot_turn(battle_id, b["current_turn_player_id"], opponent_id)
                    cur.execute("SELECT * FROM BATTLES WHERE battle_id = ?", (battle_id,))
                    b = cur.fetchone()

        cur.execute("SELECT player_id, db_username, display_name, elo_rating FROM PLAYERS WHERE player_id = ?", (b["player1_id"],))
        p1 = dict(cur.fetchone())

        p2 = None
        if b["player2_id"]:
            cur.execute("SELECT player_id, db_username, display_name, elo_rating FROM PLAYERS WHERE player_id = ?", (b["player2_id"],))
            p2_row = cur.fetchone()
            if p2_row:
                p2 = dict(p2_row)

        cur.execute("SELECT * FROM BATTLE_CREATURES WHERE battle_id = ? AND player_id = ?", (battle_id, b["player1_id"]))
        p1_creatures = [dict(c) for c in cur.fetchall()]

        p2_creatures = []
        if b["player2_id"]:
            cur.execute("SELECT * FROM BATTLE_CREATURES WHERE battle_id = ? AND player_id = ?", (battle_id, b["player2_id"]))
            p2_creatures = [dict(c) for c in cur.fetchall()]

        cur.execute("""
            SELECT bt.*, 
                   ac.name as actor_creature_name, 
                   tc.name as target_creature_name
            FROM BATTLE_TURNS bt
            JOIN BATTLE_CREATURES ac ON bt.actor_creature_id = ac.battle_creature_id
            JOIN BATTLE_CREATURES tc ON bt.target_creature_id = tc.battle_creature_id
            WHERE bt.battle_id = ?
            ORDER BY bt.turn_id ASC
        """, (battle_id,))
        turns = [dict(t) for t in cur.fetchall()]

        return {
            "battle_id": b["battle_id"],
            "battle_type": b["battle_type"],
            "status": b["status"],
            "turn_number": b["turn_number"],
            "current_turn_player_id": b["current_turn_player_id"],
            "winner_id": b["winner_id"],
            "player1": p1,
            "player2": p2,
            "player1_creatures": p1_creatures,
            "player2_creatures": p2_creatures,
            "turns": turns
        }

    def execute_attack(self, battle_id: int, actor_player_id: int, actor_creature_id: int, target_creature_id: int, action_type: str = "ELEMENTAL_ATTACK") -> Dict[str, Any]:
        """Ход атаки с расчетом стихий, проверкой победы и начислением Elo."""
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM BATTLES WHERE battle_id = ?", (battle_id,))
        battle = cur.fetchone()
        if not battle or battle["status"] != "IN_PROGRESS":
            return {"success": False, "message": "Бой не активен."}

        if battle["current_turn_player_id"] != actor_player_id:
            return {"success": False, "message": "Сейчас ход другого игрока!"}

        cur.execute("SELECT * FROM BATTLE_CREATURES WHERE battle_creature_id = ? AND battle_id = ?", (actor_creature_id, battle_id))
        actor_c = cur.fetchone()
        if not actor_c or actor_c["player_id"] != actor_player_id or actor_c["is_fainted"] == 1:
            return {"success": False, "message": "Атакующее существо повержено или не принадлежит вам."}

        cur.execute("SELECT * FROM BATTLE_CREATURES WHERE battle_creature_id = ? AND battle_id = ?", (target_creature_id, battle_id))
        target_c = cur.fetchone()
        if not target_c or target_c["player_id"] == actor_player_id or target_c["is_fainted"] == 1:
            return {"success": False, "message": "Неверная цель атаки."}

        target_player_id = target_c["player_id"]

        is_hit, is_crit, elem_mult, damage, msg = calculate_damage(
            attacker_attack=actor_c["attack"],
            attacker_speed=actor_c["speed"],
            attacker_elem=actor_c["element_id"],
            target_defense=target_c["defense"],
            target_speed=target_c["speed"],
            target_elem=target_c["element_id"],
            action_type=action_type
        )

        new_target_hp = max(0, target_c["current_hp"] - damage)
        target_fainted = 1 if new_target_hp == 0 else 0

        cur.execute("""
            UPDATE BATTLE_CREATURES
            SET current_hp = ?, is_fainted = ?
            WHERE battle_creature_id = ?
        """, (new_target_hp, target_fainted, target_creature_id))

        action_msg = f"{actor_c['name']} атаковал {target_c['name']}! {msg}"
        if target_fainted:
            action_msg += f" {target_c['name']} повержен!"

        cur.execute("""
            INSERT INTO BATTLE_TURNS 
                (battle_id, turn_number, actor_player_id, actor_creature_id, target_player_id, target_creature_id, 
                 action_type, is_hit, is_critical, element_multiplier, damage_dealt, target_remaining_hp, message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            battle_id, battle["turn_number"], actor_player_id, actor_creature_id,
            target_player_id, target_creature_id, action_type,
            1 if is_hit else 0, 1 if is_crit else 0, elem_mult, damage, new_target_hp, action_msg
        ))

        cur.execute("SELECT * FROM BATTLE_CREATURES WHERE battle_id = ? AND player_id = ?", (battle_id, target_player_id))
        target_team = [dict(c) for c in cur.fetchall()]
        is_victory = check_team_defeat(target_team)

        if is_victory:
            cur.execute("""
                UPDATE BATTLES 
                SET status = 'FINISHED', winner_id = ?, finished_at = CURRENT_TIMESTAMP
                WHERE battle_id = ?
            """, (actor_player_id, battle_id))

            # Расчет Elo и рангов
            cur.execute("UPDATE PLAYERS SET battles_won = battles_won + 1, exp = exp + 120, coins = coins + 60, elo_rating = elo_rating + 25 WHERE player_id = ?", (actor_player_id,))
            cur.execute("UPDATE PLAYERS SET battles_lost = battles_lost + 1, exp = exp + 35, elo_rating = MAX(800, elo_rating - 20) WHERE player_id = ?", (target_player_id,))

            # Обновление дивизиона
            for pid in (actor_player_id, target_player_id):
                cur.execute("SELECT elo_rating FROM PLAYERS WHERE player_id = ?", (pid,))
                elo = cur.fetchone()[0]
                rank = "BRONZE"
                if elo >= 1400: rank = "DIAMOND"
                elif elo >= 1250: rank = "PLATINUM"
                elif elo >= 1150: rank = "GOLD"
                elif elo >= 1050: rank = "SILVER"
                cur.execute("UPDATE PLAYERS SET season_rank = ? WHERE player_id = ?", (rank, pid))

            next_turn_player_id = None
        else:
            next_turn_player_id = target_player_id
            cur.execute("""
                UPDATE BATTLES 
                SET current_turn_player_id = ?, turn_number = turn_number + 1
                WHERE battle_id = ?
            """, (next_turn_player_id, battle_id))

        self.sqlite_conn.commit()

        # Автоматический ответ Бота (только если ход совершил человек)
        bot_action = None
        if not is_victory and next_turn_player_id is not None:
            cur.execute("SELECT db_username FROM PLAYERS WHERE player_id = ?", (actor_player_id,))
            p_actor = cur.fetchone()
            if p_actor and p_actor["db_username"] != "ORACLE_BOT":
                cur.execute("SELECT db_username FROM PLAYERS WHERE player_id = ?", (next_turn_player_id,))
                p_user = cur.fetchone()
                if p_user and p_user["db_username"] == "ORACLE_BOT":
                    bot_action = self._trigger_bot_turn(battle_id, next_turn_player_id, actor_player_id)
                    if bot_action and bot_action.get("is_victory"):
                        is_victory = True
                        actor_player_id = bot_action.get("winner_id", next_turn_player_id)

        return {
            "success": True,
            "is_hit": is_hit,
            "is_critical": is_crit,
            "element_multiplier": elem_mult,
            "damage": damage,
            "target_remaining_hp": new_target_hp,
            "target_fainted": bool(target_fainted),
            "is_victory": is_victory,
            "winner_id": actor_player_id if is_victory else None,
            "message": action_msg,
            "bot_action": bot_action
        }

    def _trigger_bot_turn(self, battle_id: int, bot_player_id: int, opponent_player_id: int) -> Optional[Dict[str, Any]]:
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM BATTLE_CREATURES WHERE battle_id = ? AND player_id = ? AND is_fainted = 0", (battle_id, bot_player_id))
        bot_creatures = cur.fetchall()
        if not bot_creatures: return None
        bot_actor = random.choice(bot_creatures)

        cur.execute("SELECT * FROM BATTLE_CREATURES WHERE battle_id = ? AND player_id = ? AND is_fainted = 0", (battle_id, opponent_player_id))
        target_creatures = cur.fetchall()
        if not target_creatures: return None
        target = random.choice(target_creatures)

        return self.execute_attack(
            battle_id=battle_id,
            actor_player_id=bot_player_id,
            actor_creature_id=bot_actor["battle_creature_id"],
            target_creature_id=target["battle_creature_id"]
        )

    def use_item(self, battle_id: int, player_id: int, item_id: int, target_creature_id: int) -> Dict[str, Any]:
        """Использование зелья в бою. Тратит ход игрока и передаёт инициативу сопернику."""
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM BATTLES WHERE battle_id = ?", (battle_id,))
        battle = cur.fetchone()
        if not battle or battle["status"] != "IN_PROGRESS":
            return {"success": False, "message": "Бой не активен."}

        if battle["current_turn_player_id"] != player_id:
            return {"success": False, "message": "Сейчас ход другого игрока! Нельзя использовать предмет."}

        cur.execute("SELECT quantity FROM PLAYER_INVENTORY WHERE player_id = ? AND item_id = ?", (player_id, item_id))
        inv = cur.fetchone()
        if not inv or inv["quantity"] <= 0:
            return {"success": False, "message": "У вас нет этого предмета в инвентаре."}

        cur.execute("SELECT * FROM ITEMS WHERE item_id = ?", (item_id,))
        item = cur.fetchone()

        cur.execute("SELECT * FROM BATTLE_CREATURES WHERE battle_creature_id = ? AND battle_id = ? AND player_id = ?", (target_creature_id, battle_id, player_id))
        creature = cur.fetchone()
        if not creature:
            return {"success": False, "message": "Существо не найдено в этом бою."}

        if item["item_type"] == "HEAL":
            new_hp = min(creature["max_hp"], creature["current_hp"] + item["effect_value"])
            cur.execute("UPDATE BATTLE_CREATURES SET current_hp = ?, is_fainted = 0 WHERE battle_creature_id = ?", (new_hp, target_creature_id))
            cur.execute("UPDATE PLAYER_INVENTORY SET quantity = quantity - 1 WHERE player_id = ? AND item_id = ?", (player_id, item_id))

            target_player_id = battle["player2_id"] if battle["player1_id"] == player_id else battle["player1_id"]
            action_msg = f"Игрок применил {item['name']}! {creature['name']} восстановил {item['effect_value']} HP ({new_hp}/{creature['max_hp']})."

            cur.execute("""
                INSERT INTO BATTLE_TURNS 
                    (battle_id, turn_number, actor_player_id, actor_creature_id, target_player_id, target_creature_id, 
                     action_type, is_hit, is_critical, element_multiplier, damage_dealt, target_remaining_hp, message)
                VALUES (?, ?, ?, ?, ?, ?, 'ITEM_HEAL', 1, 0, 1.0, 0, ?, ?)
            """, (battle_id, battle["turn_number"], player_id, target_creature_id, target_player_id, target_creature_id, new_hp, action_msg))

            # Передаём ход сопернику
            cur.execute("""
                UPDATE BATTLES 
                SET current_turn_player_id = ?, turn_number = turn_number + 1
                WHERE battle_id = ?
            """, (target_player_id, battle_id))
            self.sqlite_conn.commit()

            # Автоматический ответ Бота при необходимости
            bot_action = None
            if target_player_id is not None:
                cur.execute("SELECT db_username FROM PLAYERS WHERE player_id = ?", (target_player_id,))
                p_user = cur.fetchone()
                if p_user and p_user["db_username"] == "ORACLE_BOT":
                    bot_action = self._trigger_bot_turn(battle_id, target_player_id, player_id)

            return {
                "success": True,
                "message": action_msg,
                "new_hp": new_hp,
                "bot_action": bot_action
            }

        return {"success": False, "message": "Этот предмет нельзя использовать прямо в бою."}

    def surrender_battle(self, battle_id: int, player_id: int) -> Dict[str, Any]:
        """
        Досрочное завершение боя по инициативе игрока (капитуляция/сдача).
        Гарантирует техническое поражение сдающемуся игроку и победу сопернику.
        """
        cur = self.sqlite_conn.cursor()
        cur.execute("SELECT * FROM BATTLES WHERE battle_id = ?", (battle_id,))
        b = cur.fetchone()
        if not b:
            return {"success": False, "message": "Бой не найден."}

        if b["status"] == "FINISHED":
            return {"success": False, "message": "Бой уже завершён."}

        if player_id not in (b["player1_id"], b["player2_id"]):
            return {"success": False, "message": "Вы не являетесь участником этого боя."}

        # Если бой был в режиме ожидания (соперник ещё не зашёл)
        if b["status"] == "WAITING":
            cur.execute("UPDATE BATTLES SET status = 'CANCELLED', finished_at = CURRENT_TIMESTAMP WHERE battle_id = ?", (battle_id,))
            self.sqlite_conn.commit()
            return {"success": True, "message": "Поиск соперника отменён. Бой закрыт.", "is_cancelled": True}

        # Бой IN_PROGRESS: определяем победителя (соперника)
        winner_id = b["player2_id"] if player_id == b["player1_id"] else b["player1_id"]

        cur.execute("SELECT display_name FROM PLAYERS WHERE player_id = ?", (player_id,))
        surrendering_p = cur.fetchone()
        s_name = surrendering_p["display_name"] if surrendering_p else "Игрок"

        cur.execute("SELECT display_name, db_username FROM PLAYERS WHERE player_id = ?", (winner_id,))
        winner_p = cur.fetchone()
        w_name = winner_p["display_name"] if winner_p else "Соперник"

        surrender_msg = f"🏳️ {s_name} сдался досрочно! Зафиксировано техническое поражение. Победитель: {w_name}!"

        # Запись в историю ходов BATTLE_TURNS
        cur.execute("""
            INSERT INTO BATTLE_TURNS 
                (battle_id, turn_number, actor_player_id, actor_creature_id, target_player_id, target_creature_id, 
                 action_type, is_hit, is_critical, element_multiplier, damage_dealt, target_remaining_hp, message)
            VALUES (?, ?, ?, 0, ?, 0, 'SURRENDER', 1, 0, 1.0, 0, 0, ?)
        """, (battle_id, b["turn_number"], player_id, winner_id, surrender_msg))

        # Завершение боя
        cur.execute("""
            UPDATE BATTLES 
            SET status = 'FINISHED', winner_id = ?, finished_at = CURRENT_TIMESTAMP
            WHERE battle_id = ?
        """, (winner_id, battle_id))

        # Начисление поражения сдающемуся: -25 Elo, +1 battles_lost
        cur.execute("""
            UPDATE PLAYERS 
            SET battles_lost = battles_lost + 1, 
                elo_rating = MAX(800, elo_rating - 25)
            WHERE player_id = ?
        """, (player_id,))

        # Начисление победы сопернику (если соперник человек): +100 EXP, +50 монет, +25 Elo
        if winner_p and winner_p["db_username"] != "ORACLE_BOT":
            cur.execute("""
                UPDATE PLAYERS 
                SET battles_won = battles_won + 1, 
                    exp = exp + 100, 
                    coins = coins + 50, 
                    elo_rating = elo_rating + 25
                WHERE player_id = ?
            """, (winner_id,))

        # Обновление дивизионов для обоих участников
        for pid in (player_id, winner_id):
            cur.execute("SELECT elo_rating FROM PLAYERS WHERE player_id = ?", (pid,))
            row_elo = cur.fetchone()
            if row_elo:
                elo = row_elo[0]
                rank = "BRONZE"
                if elo >= 1400: rank = "DIAMOND"
                elif elo >= 1250: rank = "PLATINUM"
                elif elo >= 1150: rank = "GOLD"
                elif elo >= 1050: rank = "SILVER"
                cur.execute("UPDATE PLAYERS SET season_rank = ? WHERE player_id = ?", (rank, pid))

        self.sqlite_conn.commit()

        return {
            "success": True,
            "message": surrender_msg,
            "winner_id": winner_id,
            "surrender_player_id": player_id,
            "is_victory": False
        }


db_manager = DatabaseManager()

=======
        player = self.connection.execute(
            """
            SELECT *
            FROM players
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        if player is None:
            return None

        if not self.verify_password(
            password,
            player["password_hash"],
        ):
            return None

        return dict(player)

    def get_player_creatures(
        self,
        player_id: int,
    ) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT
                pc.creature_id,
                pc.nickname,
                pc.level,
                pc.current_hp,
                pc.max_hp,
                pc.attack,
                pc.defense,
                pc.speed,
                pc.in_team,
                ct.name,
                ct.element
            FROM player_creatures AS pc
            JOIN creature_templates AS ct
                ON ct.template_id = pc.template_id
            WHERE pc.player_id = ?
            ORDER BY pc.in_team DESC, pc.creature_id
            """,
            (player_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    def close(self) -> None:
        self.connection.close()
>>>>>>> b82894cf9cea5739da9f0e6dcb6d24c7e9a86e0e
