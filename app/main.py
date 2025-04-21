from fastapi import FastAPI
from app.route import auth, profiles, websocket_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(profiles.profile_router, prefix="/profiles")
app.include_router(websocket_router.router) # Вот  тут по идее дорога на веб сокет

app.mount("/static", StaticFiles(directory="app/static/avatars"), name="static")