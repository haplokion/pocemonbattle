"""
Pydantic-модели данных для API Покемон-баттл (Расширенная версия)
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Имя пользователя Oracle DB (например, PLAYER1 или PLAYER2)")
    password: str = Field(..., description="Пароль пользователя")


class LoginResponse(BaseModel):
    success: bool
    username: str
    display_name: str
    player_id: int
    has_game_role: bool
    role_name: str
    message: str


class RegisterRequest(BaseModel):
    username: str = Field(..., description="Логин игрока (учетная запись Oracle)")
    password: str = Field(..., description="Пароль")
    display_name: str = Field(..., description="Имя тренера")
    starter_template_id: int = Field(1, description="ID стартового покемона (1: Огонь, 6: Трава, 11: Вода, 16: Земля)")


class CreatureTemplate(BaseModel):
    template_id: int
    name: str
    element_id: str
    base_hp: int
    base_attack: int
    base_defense: int
    base_speed: int
    sprite_name: str
    unlock_level: int
    evolution_level: int
    evolves_to_id: Optional[int] = None
    description: Optional[str] = None


class PlayerCreature(BaseModel):
    creature_id: int
    player_id: int
    template_id: int
    name: str
    element_id: str
    nickname: Optional[str] = None
    level: int
    current_hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    is_in_team: bool
    evolution_level: int
    can_evolve: bool
    next_evolution_name: Optional[str] = None


class UpdateCreatureRequest(BaseModel):
    nickname: Optional[str] = None
    is_in_team: Optional[bool] = None


class EvolveCreatureRequest(BaseModel):
    creature_id: int


class CatchCreatureResponse(BaseModel):
    success: bool
    message: str
    creature: Optional[dict] = None
    remaining_coins: int


class MathChallenge(BaseModel):
    num1: int
    num2: int
    question: str


class MathSolveRequest(BaseModel):
    player_id: int
    num1: int
    num2: int
    answer: int


class MathSolveResponse(BaseModel):
    correct: bool
    message: str
    exp_gained: int
    coins_gained: int
    current_exp: int
    current_level: int
    level_up: bool


class BattleCreateRequest(BaseModel):
    player_id: int
    battle_type: str = "PVP"


class BattleJoinRequest(BaseModel):
    player_id: int


class AttackRequest(BaseModel):
    actor_player_id: int
    actor_creature_id: int
    target_creature_id: int
    action_type: str = "ELEMENTAL_ATTACK"


class UseItemRequest(BaseModel):
    player_id: int
    item_id: int
    target_creature_id: int


class BattleCreatureState(BaseModel):
    battle_creature_id: int
    player_id: int
    original_creature_id: int
    name: str
    element_id: str
    current_hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    is_fainted: bool


class TurnRecord(BaseModel):
    turn_id: int
    turn_number: int
    actor_player_id: int
    actor_creature_name: str
    target_player_id: int
    target_creature_name: str
    action_type: str
    is_hit: bool
    is_critical: bool
    element_multiplier: float
    damage_dealt: int
    target_remaining_hp: int
    message: str
    created_at: str


class LeaderboardEntry(BaseModel):
    rank: int
    player_id: int
    display_name: str
    db_username: str
    level: int
    elo_rating: int
    season_rank: str
    battles_won: int
    battles_lost: int
    win_rate: float


class SurrenderRequest(BaseModel):
    player_id: int
