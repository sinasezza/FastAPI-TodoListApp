from sqlalchemy import Column, Integer, String, Boolean
from .database import Base


class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    priority = Column(Integer)
    completed = Column(Boolean, default=False)
