"""
Главный модуль FastAPI приложения 'Покемон-баттл' (Расширенная версия)
Включает регистрацию, профиль, прокачку за таблицу умножения,
эволюцию существ, ловлю и рейтинговую таблицу лидеров.
"""
import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from . import config
from .db import db_manager
from .models import (
    LoginRequest, LoginResponse, RegisterRequest,
    BattleCreateRequest, BattleJoinRequest,
    AttackRequest, UseItemRequest,
    UpdateCreatureRequest, MathSolveRequest,
    SurrenderRequest
)

app = FastAPI(
    title="Покемон-баттл RPG (Oracle DB Edition)",
    description="Многопользовательская пошаговая RPG с 4 стихиями, эволюцией, таблицей лидеров и прокачкой",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Покемон-баттл API запущен."}


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "oracle_connected": db_manager.is_oracle_active,
        "oracle_host": config.ORACLE_HOST,
        "db_mode": config.DB_MODE
    }


# =====================================================================
# 1. АУТЕНТИФИКАЦИЯ И РЕГИСТРАЦИЯ (ТЗ 3.1)
# =====================================================================
@app.post("/api/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    result = db_manager.authenticate_player(req.username, req.password)
    return LoginResponse(**result)


@app.post("/api/auth/register", response_model=LoginResponse)
def register(req: RegisterRequest):
    result = db_manager.register_player(
        username=req.username,
        password=req.password,
        display_name=req.display_name,
        starter_template_id=req.starter_template_id
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return LoginResponse(**result)


# =====================================================================
# 2. ПРОФИЛЬ ИГРОКА, ИНВЕНТАРЬ И СУЩЕСТВА
# =====================================================================
@app.get("/api/player/{player_id}/profile")
def get_player_profile(player_id: int):
    profile = db_manager.get_player_profile(player_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Профиль игрока не найден")
    return profile


@app.get("/api/player/{player_id}/creatures")
def get_player_creatures(player_id: int):
    return db_manager.get_player_creatures(player_id)


@app.get("/api/player/{player_id}/inventory")
def get_player_inventory(player_id: int):
    return db_manager.get_player_inventory(player_id)


@app.post("/api/player/{player_id}/creatures/{creature_id}/update")
def update_creature(player_id: int, creature_id: int, req: UpdateCreatureRequest):
    result = db_manager.update_creature(
        player_id=player_id,
        creature_id=creature_id,
        nickname=req.nickname,
        is_in_team=req.is_in_team
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@app.post("/api/player/{player_id}/creatures/{creature_id}/evolve")
def evolve_creature(player_id: int, creature_id: int):
    result = db_manager.evolve_creature(player_id, creature_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@app.post("/api/player/{player_id}/creatures/catch")
def catch_creature(player_id: int):
    result = db_manager.catch_creature(player_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@app.get("/api/creatures")
def get_all_creatures():
    return db_manager.get_creatures_templates()


# =====================================================================
# 3. ПАСХАЛКА: ТАБЛИЦА УМНОЖЕНИЯ (ТРЕНИРОВКА ТРЕНЕРА)
# =====================================================================
@app.get("/api/training/math-challenge")
def get_math_challenge():
    """Генерация случайного примера на таблицу умножения для пасхалки."""
    num1 = random.randint(2, 9)
    num2 = random.randint(2, 9)
    return {
        "num1": num1,
        "num2": num2,
        "question": f"Сколько будет {num1} × {num2}?"
    }


@app.post("/api/training/math-solve")
def solve_math_challenge(req: MathSolveRequest):
    return db_manager.solve_math_challenge(
        player_id=req.player_id,
        num1=req.num1,
        num2=req.num2,
        answer=req.answer
    )


# =====================================================================
# 4. РЕЙТИНГОВАЯ ТАБЛИЦА СЕЗОНА (LEADERBOARD)
# =====================================================================
@app.get("/api/leaderboard")
def get_leaderboard():
    return db_manager.get_leaderboard()


# =====================================================================
# 5. БОИ, ЛОББИ И АТАКИ
# =====================================================================
@app.get("/api/battles")
def list_battles():
    return db_manager.list_battles()


@app.post("/api/battles/create")
def create_battle(req: BattleCreateRequest):
    battle_id = db_manager.create_battle(req.player_id, battle_type=req.battle_type)
    return {"battle_id": battle_id, "status": "WAITING", "message": "Бой создан! Ожидание второго игрока..."}


@app.post("/api/battles/{battle_id}/join")
def join_battle(battle_id: int, req: BattleJoinRequest):
    success = db_manager.join_battle(battle_id, req.player_id)
    if not success:
        raise HTTPException(status_code=400, detail="Не удалось подключиться к бою.")
    return {"success": True, "battle_id": battle_id, "message": "Успешное подключение! Бой начинается."}


@app.post("/api/battles/bot")
def start_bot_battle(req: BattleCreateRequest):
    battle_id = db_manager.create_bot_battle(req.player_id)
    return {"battle_id": battle_id, "status": "IN_PROGRESS", "message": "Тренировочный бой против ИИ начат!"}


@app.get("/api/battles/{battle_id}")
def get_battle(battle_id: int):
    state = db_manager.get_battle_state(battle_id)
    if not state:
        raise HTTPException(status_code=404, detail="Бой не найден")
    return state


@app.post("/api/battles/{battle_id}/attack")
def attack(battle_id: int, req: AttackRequest):
    result = db_manager.execute_attack(
        battle_id=battle_id,
        actor_player_id=req.actor_player_id,
        actor_creature_id=req.actor_creature_id,
        target_creature_id=req.target_creature_id,
        action_type=req.action_type
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Ошибка хода"))
    return result


@app.post("/api/battles/{battle_id}/use_item")
def use_item(battle_id: int, req: UseItemRequest):
    result = db_manager.use_item(
        battle_id=battle_id,
        player_id=req.player_id,
        item_id=req.item_id,
        target_creature_id=req.target_creature_id
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result


@app.post("/api/battles/{battle_id}/surrender")
def surrender_battle(battle_id: int, req: SurrenderRequest):
    result = db_manager.surrender_battle(battle_id, req.player_id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Не удалось сдаться"))
    return result
