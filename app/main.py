import app.security.jwt_auth
from fastapi import FastAPI
from app.route import refresh, protected
from app.security import login, registration

app = FastAPI()

app.include_router(login.router)
app.include_router(registration.router)
app.include_router(refresh.router)
app.include_router(protected.router)