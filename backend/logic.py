mport random
from typing import Dict, Tuple, List, Optional

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

ELEMENT_NAMES: Dict[str, str] = {
    "FIRE": "Огонь 🔥",
    "GRASS": "Трава 🌿",
    "WATER": "Вода 💧",
    "EARTH": "Земля ⛰️",
}


def get_element_multiplier(attacker_elem: str, defender_elem: str) -> float:
    attacker_elem = attacker_elem.upper()
    defender_elem = defender_elem.upper()
    return ELEMENTAL_MULTIPLIERS.get(attacker_elem, {}).get(defender_elem, 1.0)


def calculate_hit(attacker_speed: int, defender_speed: int) -> bool:
    speed_diff = attacker_speed - defender_speed
    hit_chance = max(70, min(98, 92 + int(speed_diff * 0.4)))
    roll = random.randint(1, 100)
    return roll <= hit_chance


def calculate_critical(attacker_speed: int) -> bool:
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

    is_hit = calculate_hit(attacker_speed, target_speed)
    if not is_hit:
        return False, False, 1.0, 0, "Промах! Быстрое существо противника уклонилось от удара!"

    elem_multiplier = get_element_multiplier(attacker_elem, target_elem)

    is_critical = calculate_critical(attacker_speed)
    crit_multiplier = 1.5 if is_critical else 1.0

    base_damage = max(6, int((attacker_attack * 1.55) - (target_defense * 0.55)))

    variance = random.uniform(0.92, 1.08)

    total_damage = max(1, int(base_damage * elem_multiplier * crit_multiplier * variance))
