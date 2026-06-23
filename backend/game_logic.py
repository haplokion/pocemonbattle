"""
Модуль боевой логики 'Покемон-баттл'
Включает стихийную систему (Огонь, Трава, Вода, Земля),
расчёт точности, критического урона, модификаторов и проверку завершения боя.
"""
import random
from typing import Dict, Tuple, List, Optional

# Матрица стихийных множителей урона
ELEMENTAL_MULTIPLIERS: Dict[str, Dict[str, float]] = {
    "FIRE": {
        "FIRE": 1.0,
        "GRASS": 1.5,
        "WATER": 0.7,
        "EARTH": 1.1,
    },
    "GRASS": {
        "FIRE": 0.7,
        "GRASS": 1.0,
        "WATER": 1.5,
        "EARTH": 1.4,
    },
    "WATER": {
        "FIRE": 1.5,
        "GRASS": 0.7,
        "WATER": 1.0,
        "EARTH": 1.2,
    },
    "EARTH": {
        "FIRE": 1.4,
        "GRASS": 0.7,
        "WATER": 1.0,
        "EARTH": 1.0,
    }
}

# Описания стихий на русском
ELEMENT_NAMES: Dict[str, str] = {
    "FIRE": "Огонь 🔥",
    "GRASS": "Трава 🌿",
    "WATER": "Вода 💧",
    "EARTH": "Земля ⛰️",
}


def get_element_multiplier(attacker_elem: str, defender_elem: str) -> float:
    """Возвращает стихийный множитель урона."""
    attacker_elem = attacker_elem.upper()
    defender_elem = defender_elem.upper()
    return ELEMENTAL_MULTIPLIERS.get(attacker_elem, {}).get(defender_elem, 1.0)


def calculate_hit(attacker_speed: int, defender_speed: int) -> bool:
    """
    Расчёт попадания или промаха.
    Базовый шанс 92%, корректируется разницей в скорости.
    """
    speed_diff = attacker_speed - defender_speed
    hit_chance = max(70, min(98, 92 + int(speed_diff * 0.4)))
    roll = random.randint(1, 100)
    return roll <= hit_chance


def calculate_critical(attacker_speed: int) -> bool:
    """Шанс критического удара (базовый 12% + бонус за скорость)."""
    crit_chance = max(8, min(35, 12 + int(attacker_speed * 0.2)))
    roll = random.randint(1, 100)
    return roll <= crit_chance


def calculate_damage(
    attacker_attack: int,
    attacker_speed: int,
    attacker_elem: str,
    target_defense: int,
    target_speed: int,
    target_elem: str,
    action_type: str = "ELEMENTAL_ATTACK"
) -> Tuple[bool, bool, float, int, str]:
    """
    Полный расчёт хода атаки.
    Возвращает:
      - is_hit: попал ли
      - is_critical: критический ли удар
      - elem_multiplier: стихийный множитель
      - damage: нанесённый урон
      - message_desc: комментарий к результату атаки
    """
    # 1. Проверка попадания
    is_hit = calculate_hit(attacker_speed, target_speed)
    if not is_hit:
        return False, False, 1.0, 0, "Промах! Быстрое существо противника уклонилось от удара!"

    # 2. Стихийный множитель
    elem_multiplier = get_element_multiplier(attacker_elem, target_elem)

    # 3. Критический удар
    is_critical = calculate_critical(attacker_speed)
    crit_multiplier = 1.5 if is_critical else 1.0

    # 4. Базовый урон формулы RPG:
    # Базовый урон учитывает силу атаки атакующего и защиту цели
    base_damage = max(6, int((attacker_attack * 1.55) - (target_defense * 0.55)))

    # Небольшой случайный разброс (variance 0.92 - 1.08)
    variance = random.uniform(0.92, 1.08)

    total_damage = max(1, int(base_damage * elem_multiplier * crit_multiplier * variance))

    # Формирование комментария
    notes = []
    if elem_multiplier >= 1.4:
        notes.append("Стихийное преимущество! (x{:.1f})".format(elem_multiplier))
    elif elem_multiplier <= 0.75:
        notes.append("Стихийное сопротивление! (x{:.1f})".format(elem_multiplier))

    if is_critical:
        notes.append("Критический удар! (x1.5)")

    desc = f"Нанесено {total_damage} ед. урона."
    if notes:
        desc += " [" + ", ".join(notes) + "]"

    return True, is_critical, elem_multiplier, total_damage, desc


def check_team_defeat(creatures: List[dict]) -> bool:
    """Проверяет, повержены ли все существа в команде игрока."""
    if not creatures:
        return False
    return all(c.get("current_hp", 0) <= 0 or c.get("is_fainted", False) for c in creatures)
