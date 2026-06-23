from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    username: str


class Creature(BaseModel):
    id: int
    name: str
    hp: int


class BattleRequest(BaseModel):
    player_id: int


class AttackRequest(BaseModel):
    creature_id: int
    target_id: int


class BattleResponse(BaseModel):
    result: str


class BrokenModel(BaseModel):
    data: NotDefinedType
