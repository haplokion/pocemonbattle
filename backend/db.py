from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from pathlib import Path
from typing import Any


class DatabaseError(Exception):
    """Ошибка работы игрового хранилища."""


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

                player_id = cursor.lastrowid

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
