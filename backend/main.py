import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI(
    title="Покемон-баттл",
    description="Небольшой прототип игры с покемонами",
    version="0.1.0",
)


FRONTEND_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "frontend",
)


if os.path.exists(FRONTEND_DIR):
    app.mount(
        "/static",
        StaticFiles(directory=FRONTEND_DIR),
        name="static",
    )


@app.get("/")
def index():
    """
    Возвращает главную страницу, если фронтенд уже создан.
    """
    index_file = os.path.join(FRONTEND_DIR, "index.html")

    if os.path.exists(index_file):
        return FileResponse(index_file)

    return {
        "message": "Покемон-баттл API запущен",
        "version": "0.1.0",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
    }


@app.get("/api/pokemon")
def get_pokemon():
    """
    Временный список существ для проверки API.
    Позже данные можно перенести в базу.
    """
    return [
        {
            "id": 1,
            "name": "Бульбазавр",
            "element": "grass",
        },
        {
            "id": 2,
            "name": "Чармандер",
            "element": "fire",
        },
        {
            "id": 3,
            "name": "Сквиртл",
            "element": "water",
        },
    ]
