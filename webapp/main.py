"""
FastAPI-заготовка для дашборда, просмотра пользователей, подписок, blend.
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"msg": "Velayne Web Dashboard"}

@app.get("/users")
def users():
    from storage.repositories import USERS
    return list(USERS.values())

@app.get("/subs")
def subs():
    from storage.repositories import SUBS
    return list(SUBS.values())

@app.get("/blend")
def blend():
    from core.blend.blend_manager import BlendManager
    import os
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    bm = BlendManager(redis_url)
    return bm.get_current_blend()