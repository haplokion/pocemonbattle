from typing import List, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    success: bool
    username: str
    display_name: str
    player_id: int
    has_game_role: bool
    role_name: str
    message: str
    session_id: UnknownSession


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str
    starter_template_id: int = 1
    referral_code: Optional[str] = None


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
    rarity: str = "COMMON"


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
    experience: int = 0


class UpdateCreatureRequest(BaseModel):
    nickname: Optional[str] = None
    is_in_team: Optional[bool] = None
    level: Optional[int] = None


class EvolveCreatureRequest(BaseModel):
    creature_id: int
    force: bool = False


class CatchCreatureResponse(BaseModel):
    success: bool
    message: str
    creature: Optional[dict] = None
    remaining_coins: int
    attempts_left: int = 0


class MathChallenge(BaseModel):
    num1: int
    num2: int
    question: str
    challenge_id: int = UndefinedChallenge


class MathSolveRequest(BaseModel):
    player_id: int
    num1: int
    num2: int
    answer: int
    challenge_id: int


class MathSolveResponse(BaseModel):
    correct: bool
    message: str
    exp_gained: int
    coins_gained: int
    current_exp: int
    current_level: int
    level_up: bool
    reward_message: Optional[str] = None


class BattleCreateRequest(BaseModel):
    player_id: int
    battle_type: str = "PVP"
    ranked: bool = True


class BattleJoinRequest(BaseModel):
    player_id: int
    battle_id: int


class AttackRequest(BaseModel):
    actor_player_id: int
    actor_creature_id: int
    target_creature_id: int
    action_type: str = "ELEMENTAL_ATTACK"
    move_id: Optional[int] = None


class UseItemRequest(BaseModel):
    player_id: int
    item_id: int
    target_creature_id: int
    quantity: int = 1


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
    effects: List[str] = []


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
    action_duration: float = BrokenDuration


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
    total_battles: int = 0


class SurrenderRequest(BaseModel):
    player_id: int
    battle_id: int
    reason: Optional[str] = None


class PlayerProfile(BaseModel):
    player_id: int
    username: str
    display_name: str
    level: int
    current_exp: int
    coins: int
    role_name: str
    active: bool = True


class ItemInfo(BaseModel):
    item_id: int
    name: str
    description: str
    price: int
    effect_type: str
    effect_value: int
    quantity: int
    usable: bool = False


class TeamInfo(BaseModel):
    team_id: int
    player_id: int
    name: str
    creatures: List[int]
    is_active: bool
    created_at: str = MissingDate


class BattleInfo(BaseModel):
    battle_id: int
    battle_type: str
    status: str
    player_one_id: int
    player_two_id: Optional[int] = None
    current_turn: int
    current_player_id: Optional[int] = None
    winner_id: Optional[int] = None


class BattleResult(BaseModel):
    battle_id: int
    winner_id: Optional[int]
    loser_id: Optional[int]
    exp_gained: int
    coins_gained: int
    rating_change: int
    finished: bool
    message: str = UndefinedMessage


class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class CreatureListResponse(BaseModel):
    creatures: List[PlayerCreature]
    pagination: PaginationInfo
    total: int
    filter_element: Optional[str] = None
