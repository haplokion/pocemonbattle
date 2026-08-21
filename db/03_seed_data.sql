-- =====================================================================
-- ПОКЕМОН-БАТТЛ: Начальные данные (Стихии, Шаблоны Эволюции, Предметы)
-- Файл: db/03_seed_data.sql
-- =====================================================================

-- 1. СТИХИИ
INSERT INTO ELEMENTS (element_id, name_ru, color_hex, icon, description) VALUES
('FIRE', 'Огонь', '#ff4d4f', '🔥', 'Яростное пламя. Эффективен против Травы, уязвим перед Водой.');
INSERT INTO ELEMENTS (element_id, name_ru, color_hex, icon, description) VALUES
('GRASS', 'Трава', '#52c41a', '🌿', 'Сила живой природы. Эффективна против Воды и Земли, уязвима перед Огнем.');
INSERT INTO ELEMENTS (element_id, name_ru, color_hex, icon, description) VALUES
('WATER', 'Вода', '#1890ff', '💧', 'Сокрушительный прилив. Эффективна против Огня, уязвима перед Травой.');
INSERT INTO ELEMENTS (element_id, name_ru, color_hex, icon, description) VALUES
('EARTH', 'Земля', '#d48806', '⛰️', 'Несокрушимая твердь. Эффективна против Огня, уязвима перед Травой.');

-- 2. МАТРИЦА СТИХИЙНОГО УРОНА
INSERT INTO ELEMENT_ADVANTAGES VALUES ('FIRE', 'FIRE', 1.0);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('FIRE', 'GRASS', 1.5);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('FIRE', 'WATER', 0.7);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('FIRE', 'EARTH', 1.1);

INSERT INTO ELEMENT_ADVANTAGES VALUES ('GRASS', 'GRASS', 1.0);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('GRASS', 'FIRE', 0.7);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('GRASS', 'WATER', 1.5);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('GRASS', 'EARTH', 1.4);

INSERT INTO ELEMENT_ADVANTAGES VALUES ('WATER', 'WATER', 1.0);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('WATER', 'FIRE', 1.5);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('WATER', 'GRASS', 0.7);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('WATER', 'EARTH', 1.2);

INSERT INTO ELEMENT_ADVANTAGES VALUES ('EARTH', 'EARTH', 1.0);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('EARTH', 'FIRE', 1.4);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('EARTH', 'GRASS', 0.7);
INSERT INTO ELEMENT_ADVANTAGES VALUES ('EARTH', 'WATER', 1.0);

-- 3. ШАБЛОНЫ СУЩЕСТВ С ДРЕВОМ ЭВОЛЮЦИИ
-- ОГОНЬ: Игнизавр -> Инфернозавр -> Дракопир
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(1, 'Игнизавр', 'FIRE', 100, 36, 20, 26, 'ignisaur', 1, 6, 2, 'Базовый огненный ящер. Эволюционирует на 6 уровне в Инфернозавра.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(2, 'Инфернозавр', 'FIRE', 140, 52, 28, 34, 'infernosaur', 3, 12, 3, 'Вторая стадия ящера, пылающая лавой. Эволюционирует на 12 уровне.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(3, 'Дракопир', 'FIRE', 185, 70, 38, 45, 'dracopyr', 6, 0, NULL, 'Легендарный огненный дракон. Финальная форма.');

-- ОГОНЬ (СКОРОСТЬ): Пироликс -> Вулканикс
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(4, 'Пироликс', 'FIRE', 85, 42, 16, 35, 'pyrolix', 1, 7, 5, 'Быстрый огненный лис. Эволюционирует на 7 уровне.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(5, 'Вулканикс', 'FIRE', 125, 62, 24, 52, 'vulcanix', 4, 0, NULL, 'Девятихвостый дух вулканов с колоссальной скоростью.');

-- ТРАВА: Листокрыл -> Флораптерикс -> Сильванозавр
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(6, 'Листокрыл', 'GRASS', 110, 28, 28, 24, 'leafwing', 1, 6, 7, 'Лесное существо с острыми крыльями. Эволюционирует на 6 уровне.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(7, 'Флораптерикс', 'GRASS', 150, 42, 39, 32, 'florapteryx', 3, 12, 8, 'Огромный лесной ящер с изумрудным оперением.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(8, 'Сильванозавр', 'GRASS', 195, 58, 52, 40, 'sylvanosaur', 6, 0, NULL, 'Древний владыка первозданных лесов. Финальная форма.');

-- ТРАВА (ЗАЩИТА): Флоразавр -> Древозавр
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(9, 'Флоразавр', 'GRASS', 130, 26, 32, 18, 'florasaur', 1, 7, 10, 'Бронированный растительный титан.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(10, 'Древозавр', 'GRASS', 180, 40, 48, 24, 'trevezavr', 4, 0, NULL, 'Живая крепость из реликтовых деревьев.');

-- ВОДА: Аквадонт -> Левиадон -> Океанор
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(11, 'Аквадонт', 'WATER', 115, 31, 24, 25, 'aquadont', 1, 6, 12, 'Панцирный страж приливов. Эволюционирует на 6 уровне.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(12, 'Левиадон', 'WATER', 155, 46, 35, 33, 'leviadon', 3, 12, 13, 'Глубоководный змей приливов.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(13, 'Океанор', 'WATER', 200, 64, 46, 42, 'oceanor', 6, 0, NULL, 'Повелитель всех океанских пучин. Финальная форма.');

-- ВОДА (АТАКА): Гидрошторм -> Цунамикс
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(14, 'Гидрошторм', 'WATER', 95, 39, 19, 32, 'hydrostorm', 1, 7, 15, 'Водный элементаль молниеносных атак.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(15, 'Цунамикс', 'WATER', 135, 58, 28, 46, 'tsunamix', 4, 0, NULL, 'Воплощение сокрушительной волны цунами.');

-- ЗЕМЛЯ: Террагот -> Титанорок -> Геоколосс
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(16, 'Террагот', 'EARTH', 140, 27, 36, 16, 'terragoth', 1, 6, 17, 'Каменный страж гор. Эволюционирует на 6 уровне.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(17, 'Титанорок', 'EARTH', 190, 42, 52, 22, 'titanorok', 3, 12, 18, 'Монолитный титан гранитной твердыни.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(18, 'Геоколосс', 'EARTH', 240, 56, 68, 26, 'geocoloss', 6, 0, NULL, 'Живая гора. Непробиваемая броня и колоссальное HP.');

-- ЗЕМЛЯ (УДАР): Сейсморог -> Магмарог
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(19, 'Сейсморог', 'EARTH', 120, 35, 30, 21, 'seismoroc', 1, 7, 20, 'Скалистый зверь с гранитным рогом.');
INSERT INTO CREATURE_TEMPLATES (template_id, name, element_id, base_hp, base_attack, base_defense, base_speed, sprite_name, unlock_level, evolution_level, evolves_to_id, description) VALUES
(20, 'Магмарог', 'EARTH', 165, 54, 44, 29, 'magmaroc', 4, 0, NULL, 'Зверь из застывшей магмы и базальта.');

-- 4. ПРЕДМЕТЫ
INSERT INTO ITEMS (name, item_type, effect_value, description) VALUES
('Малое зелье здоровья', 'HEAL', 40, 'Восстанавливает 40 единиц здоровья выбранному существу.');
INSERT INTO ITEMS (name, item_type, effect_value, description) VALUES
('Большое зелье здоровья', 'HEAL', 80, 'Восстанавливает 80 единиц здоровья выбранному существу.');
INSERT INTO ITEMS (name, item_type, effect_value, description) VALUES
('Камень Эволюции', 'EVO_STONE', 1, 'Мистический камень, мгновенно повышающий уровень существа на +1.');

-- 5. ТЕСТОВЫЕ ИГРОКИ (PLAYER1, PLAYER2, Мастера Сезона)
INSERT INTO PLAYERS (db_username, password_hash, display_name, level, exp, coins, elo_rating, season_rank, battles_won, battles_lost) VALUES
('PLAYER1', 'Player1Password#123', 'Эш Мастер (PLAYER1)', 5, 450, 250, 1120, 'SILVER', 8, 2);

INSERT INTO PLAYERS (db_username, password_hash, display_name, level, exp, coins, elo_rating, season_rank, battles_won, battles_lost) VALUES
('PLAYER2', 'Player2Password#123', 'Гари Чемпион (PLAYER2)', 5, 520, 300, 1160, 'GOLD', 11, 3);

INSERT INTO PLAYERS (db_username, password_hash, display_name, level, exp, coins, elo_rating, season_rank, battles_won, battles_lost) VALUES
('CYBER_CHAMP', 'champ123', 'Рейн Мастер (Топ-1)', 10, 3200, 1200, 1450, 'DIAMOND', 35, 4);

-- Стартовые команды
INSERT INTO PLAYER_CREATURES (player_id, template_id, nickname, level, current_hp, max_hp, attack, defense, speed, is_in_team)
SELECT p.player_id, 1, 'Игнизавр', 5, 120, 120, 41, 23, 28, 1 FROM PLAYERS p WHERE p.db_username = 'PLAYER1';
INSERT INTO PLAYER_CREATURES (player_id, template_id, nickname, level, current_hp, max_hp, attack, defense, speed, is_in_team)
SELECT p.player_id, 6, 'Листокрыл', 5, 130, 130, 33, 31, 26, 1 FROM PLAYERS p WHERE p.db_username = 'PLAYER1';
INSERT INTO PLAYER_CREATURES (player_id, template_id, nickname, level, current_hp, max_hp, attack, defense, speed, is_in_team)
SELECT p.player_id, 11, 'Аквадонт', 5, 135, 135, 36, 27, 27, 1 FROM PLAYERS p WHERE p.db_username = 'PLAYER1';

INSERT INTO PLAYER_CREATURES (player_id, template_id, nickname, level, current_hp, max_hp, attack, defense, speed, is_in_team)
SELECT p.player_id, 4, 'Пироликс', 5, 105, 105, 47, 19, 37, 1 FROM PLAYERS p WHERE p.db_username = 'PLAYER2';
INSERT INTO PLAYER_CREATURES (player_id, template_id, nickname, level, current_hp, max_hp, attack, defense, speed, is_in_team)
SELECT p.player_id, 9, 'Флоразавр', 5, 150, 150, 31, 35, 20, 1 FROM PLAYERS p WHERE p.db_username = 'PLAYER2';
INSERT INTO PLAYER_CREATURES (player_id, template_id, nickname, level, current_hp, max_hp, attack, defense, speed, is_in_team)
SELECT p.player_id, 19, 'Сейсморог', 5, 140, 140, 40, 33, 23, 1 FROM PLAYERS p WHERE p.db_username = 'PLAYER2';

-- Инвентарь
INSERT INTO PLAYER_INVENTORY (player_id, item_id, quantity)
SELECT p.player_id, 1, 3 FROM PLAYERS p WHERE p.db_username IN ('PLAYER1', 'PLAYER2');
INSERT INTO PLAYER_INVENTORY (player_id, item_id, quantity)
SELECT p.player_id, 3, 2 FROM PLAYERS p WHERE p.db_username IN ('PLAYER1', 'PLAYER2');

COMMIT;
