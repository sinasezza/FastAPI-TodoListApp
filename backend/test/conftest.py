from typing import Callable

import pytest
from pydantic import BaseModel

from ..models import Todos, Users
from ..routers.auth import bcrypt_context
from . import utils


@pytest.fixture
def test_todo():
    todo = Todos(
        title="learn to code",
        description="some description",
        priority=1,
        completed=False,
        owner_id=1,
    )

    db = utils.TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo

    with utils.engine.connect() as connection:
        connection.execute(utils.text("DELETE FROM todos WHERE 1=1;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username="testuser",
        email="testemail@test.com",
        hashed_password=bcrypt_context.hash("testpass"),
        role="admin",
        phone_number="1234567890",
    )

    db = utils.TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    with utils.engine.connect() as connection:
        connection.execute(utils.text("DELETE FROM users WHERE 1=1;"))
        connection.commit()
