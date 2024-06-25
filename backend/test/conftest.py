import pytest
from pydantic import BaseModel
from typing import Callable
from . import utils



@pytest.fixture
def test_todo():
    todo = utils.Todos(
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
        connection.execute(utils.text("DELETE FROM todos where 1=1;"))
        connection.commit()