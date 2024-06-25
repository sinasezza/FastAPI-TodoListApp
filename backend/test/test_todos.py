import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from .. import config as env_config
from ..database import Base
from ..main import app
from ..routers.todos import get_db, get_current_user


SQLALCHEMY_TEST_DATABASE_URL = env_config.TEST_DATABASE_URL


engine = create_engine(
    url=SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"username": "testuser", "id": 1, "user_role": "admin"}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_read_all_authenticated():
    async with AsyncClient(transport=transport) as client:
        response = await client.get("http://127.0.0.1:8000/todos/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
