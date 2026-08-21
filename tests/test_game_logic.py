"""
Модульные тесты для проверки боевой логики и стихийной системы
"""
try:
    import pytest
except ImportError:
    pytest = None
from backend.game_logic import (
    get_element_multiplier,
    calculate_hit,
    calculate_critical,
    calculate_damage,
    check_team_defeat,
    ELEMENTAL_MULTIPLIERS
)


def test_elemental_multipliers():
    """Проверка матрицы стихий (Огонь, Трава, Вода, Земля)"""
    # Огонь бьет Траву
    assert get_element_multiplier("FIRE", "GRASS") == 1.5
    # Огонь слаб против Воды
    assert get_element_multiplier("FIRE", "WATER") == 0.7

    # Вода бьет Огонь
    assert get_element_multiplier("WATER", "FIRE") == 1.5
    # Вода слаба против Травы
    assert get_element_multiplier("WATER", "GRASS") == 0.7

    # Трава бьет Воду и Землю
    assert get_element_multiplier("GRASS", "WATER") == 1.5
    assert get_element_multiplier("GRASS", "EARTH") == 1.4

    # Земля бьет Огонь
    assert get_element_multiplier("EARTH", "FIRE") == 1.4


def test_same_element_multiplier():
    """Сражение существ одной стихии имеет нейтральный множитель 1.0"""
    for elem in ["FIRE", "GRASS", "WATER", "EARTH"]:
        assert get_element_multiplier(elem, elem) == 1.0


def test_damage_calculation_with_advantage():
    """Проверка повышенного урона при стихийном преимуществе"""
    # Огонь против Травы
    is_hit, is_crit, mult, damage_adv, desc = calculate_damage(
        attacker_attack=40,
        attacker_speed=25,
        attacker_elem="FIRE",
        target_defense=20,
        target_speed=20,
        target_elem="GRASS"
    )
    assert mult == 1.5
    if is_hit:
        assert damage_adv > 20
        assert "Стихийное преимущество" in desc


def test_team_defeat():
    """Проверка условия поражения команды (все HP <= 0)"""
    living_team = [
        {"name": "Игнизавр", "current_hp": 0, "is_fainted": True},
        {"name": "Листокрыл", "current_hp": 45, "is_fainted": False},
    ]
    assert check_team_defeat(living_team) is False

    fainted_team = [
        {"name": "Игнизавр", "current_hp": 0, "is_fainted": True},
        {"name": "Листокрыл", "current_hp": 0, "is_fainted": True},
    ]
    assert check_team_defeat(fainted_team) is True
    assert check_team_defeat([]) is False
