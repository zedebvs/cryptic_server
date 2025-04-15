from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()