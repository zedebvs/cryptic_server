from fastapi import FastAPI
from app.route import auth
from fastapi.staticfiles import StaticFiles
from app.route import profiles

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(profiles.profile_router, prefix="/profiles")

app.mount("/static", StaticFiles(directory="app/static/avatars"), name="static")