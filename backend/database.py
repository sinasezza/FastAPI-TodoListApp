from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from . import config


SQLALCHEMY_DATABASE_URL = config.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
