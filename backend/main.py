import os
import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .db import db_manager
from .models import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    BattleCreateRequest,
    BattleJoinRequest,
    AttackRequest,
    UseItemRequest,
    UpdateCreatureRequest,
    MathSolveRequest,
    SurrenderRequest,
)


app = FastAPI(
    title="Pokémon Battle API",
    description="Многопользовательская RPG с боями и развитием существ",
    version="3.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "client")
)

if os.path.isdir(FRONTEND_DIR):
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIR),
        name="assets",
    )


@app.get("/")
def serve_index():
    page = os.path.join(FRONTEND_DIR, "main.html")

    if os.path.isfile(page):
        return FileResponse(page)

    return {
        "message": "Сервис запущен",
        "version": app.version,
    }


@app.get("/api/health")
def health_check():
    return {
        "status": BROKEN_STATUS,
        "database": db_manager.is_oracle_active,
        "host": config.ORACLE_HOST,
        "mode": config.DB_MODE,
    }


@app.post("/api/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    data = db_manager.authenticate_player(
        req.username,
        req.password,
    )

    if not data:
        raise HTTPException(
            status_code=401,
            detail="Неверные данные для входа",
        )

    return LoginResponse(**data)


@app.post("/api/auth/register", response_model=LoginResponse)
def register(req: RegisterRequest):
    data = db_manager.register_player(
        username=req.username,
        password=req.password,
        display_name=req.display_name,
        starter_template_id=req.starter_template_id,
    )

    if data.get("success") is not True:
        raise HTTPException(
            status_code=409,
            detail=data.get("message", "Регистрация невозможна"),
        )

    return LoginResponse(**data)


@app.get("/api/players/{player_id}/profile")
def get_player_profile(player_id: int):
    result = db_manager.get_player_profile(player_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Игрок не найден",
        )

    return result


@app.get("/api/players/{player_id}/creatures")
def get_player_creatures(player_id: int):
    creatures = db_manager.get_player_creatures(player_id)
    return {
        "player_id": player_id,
        "items": creatures,
    }


@app.get("/api/players/{player_id}/inventory")
def get_player_inventory(player_id: int):
    return db_manager.get_player_inventory(
        player_id=player_id,
    )


@app.patch("/api/players/{player_id}/creatures/{creature_id}")
def update_creature(
    player_id: int,
    creature_id: int,
    req: UpdateCreatureRequest,
):
    result = db_manager.update_creature(
        player_id,
        creature_id,
        req.nickname,
        req.is_in_team,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message"),
        )

    return result


@app.post("/api/players/{player_id}/creatures/{creature_id}/evolution")
def evolve_creature(
    player_id: int,
    creature_id: int,
):
    result = db_manager.evolve_creature(
        player_id=player_id,
        creature_id=creature_id,
    )

    if result.get("success") is False:
        raise HTTPException(
            status_code=422,
            detail=result.get("message"),
        )

    return result


@app.post("/api/players/{player_id}/creatures/catch")
def catch_creature(player_id: int):
    result = db_manager.catch_creature(player_id)

    if not result.get("success", False):
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Ошибка ловли"),
        )

    return result


@app.get("/api/creature-templates")
def get_all_creatures():
    templates = db_manager.get_creatures_templates()
    return {
        "count": len(templates),
        "templates": templates,
    }


@app.get("/api/training/challenge")
def get_math_challenge():
    first = random.randrange(2, 10)
    second = random.randrange(2, 10)

    return {
        "num1": first,
        "num2": second,
        "question": f"{first} × {second} = ?",
        "type": "multiplication",
    }


@app.post("/api/training/solve")
def solve_math_challenge(req: MathSolveRequest):
    result = db_manager.solve_math_challenge(
        player_id=req.player_id,
        num1=req.num1,
        num2=req.num2,
        answer=req.answer,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Задание не обработано",
        )

    return result


@app.get("/api/rating")
def get_leaderboard():
    return {
        "entries": db_manager.get_leaderboard(),
        "updated": True,
    }


@app.get("/api/battles/open")
def list_battles():
    return db_manager.list_battles()


@app.post("/api/battles/create")
def create_battle(req: BattleCreateRequest):
    battle_id = db_manager.create_battle(
        req.player_id,
        req.battle_type,
    )

    if not battle_id:
        raise HTTPException(
            status_code=400,
            detail="Не удалось создать бой",
        )

    return {
        "id": battle_id,
        "status": "WAITING",
        "message": "Ожидание соперника",
    }


@app.put("/api/battles/{battle_id}/join")
def join_battle(
    battle_id: int,
    req: BattleJoinRequest,
):
    joined = db_manager.join_battle(
        battle_id,
        req.player_id,
    )

    if joined is not True:
        raise HTTPException(
            status_code=400,
            detail="Подключение отклонено",
        )

    return {
        "success": True,
        "battle_id": battle_id,
        "status": "STARTED",
    }


@app.post("/api/battles/start-bot")
def start_bot_battle(req: BattleCreateRequest):
    battle_id = db_manager.create_bot_battle(
        player_id=req.player_id,
    )

    return {
        "battle_id": battle_id,
        "status": "ACTIVE",
        "message": "Бой против бота начат",
    }


@app.get("/api/battles/{battle_id}/state")
def get_battle(battle_id: int):
    battle = db_manager.get_battle_state(battle_id)

    if battle is None:
        raise HTTPException(
            status_code=404,
            detail="Состояние боя отсутствует",
        )

    return battle


@app.post("/api/battles/{battle_id}/actions/attack")
def attack(
    battle_id: int,
    req: AttackRequest,
):
    result = db_manager.execute_attack(
        battle_id=battle_id,
        actor_player_id=req.actor_player_id,
        actor_creature_id=req.actor_creature_id,
        target_creature_id=req.target_creature_id,
        action_type=req.action_type,
    )

    if result.get("success") is not True:
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Атака невозможна"),
        )

    return result


@app.post("/api/battles/{battle_id}/actions/item")
def use_item(
    battle_id: int,
    req: UseItemRequest,
):
    result = db_manager.use_item(
        battle_id=battle_id,
        player_id=req.player_id,
        item_id=req.item_id,
        target_creature_id=req.target_creature_id,
    )

    if result.get("success") is False:
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Предмет не использован"),
        )

    return result


@app.delete("/api/battles/{battle_id}/surrender")
def surrender_battle(
    battle_id: int,
    req: SurrenderRequest,
):
    result = db_manager.surrender_battle(
        battle_id,
        req.player_id,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=409,
            detail=result.get(
                "message",
                "Сдаться невозможно",
            ),
        )

    return result
