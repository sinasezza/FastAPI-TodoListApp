from fastapi import status
from httpx import AsyncClient
from ..main import app
from ..models import Todos
from ..routers.todos import get_db, get_current_user
from . import utils


app.dependency_overrides[get_db] = utils.override_get_db
app.dependency_overrides[get_current_user] = utils.override_get_current_user


async def test_read_all_todos_authenticated(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.get("http://127.0.0.1:8000/todos/")
        print(f"response is {response}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": 1,
                "title": "learn to code",
                "description": "some description",
                "priority": 1,
                "completed": False,
                "owner_id": 1,
            }
        ]


async def test_read_one_todo_authenticated_should_not_found(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.get("http://127.0.0.1:8000/todos/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_read_one_todo_authenticated(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.get("http://127.0.0.1:8000/todos/1/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "title": "learn to code",
            "description": "some description",
            "priority": 1,
            "completed": False,
        }


async def test_create_todo_authenticated(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        request_data = {
            "title": "New Todo",
            "description": "some description",
            "priority": 5,
            "completed": False,
        }
        response = await client.post("http://127.0.0.1:8000/todos/", json=request_data)
        assert response.status_code == status.HTTP_201_CREATED

        db = utils.TestingSessionLocal()
        model = db.query(Todos).filter(Todos.id == 2).first()
        assert model.title == "New Todo"
        assert model.description == "some description"
        assert model.priority == 5
        assert not model.completed
        db.close()


async def test_update_todo_not_found(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        request_data = {
            "title": "New Todo2",
            "description": "some description",
            "priority": 4,
            "completed": True,
        }

        response = await client.put(
            "http://127.0.0.1:8000/todos/1000/", json=request_data
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_update_todo(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        request_data = {
            "title": "New Todo2",
            "description": "some description",
            "priority": 4,
            "completed": True,
        }

        response = await client.put("http://127.0.0.1:8000/todos/1/", json=request_data)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        db = utils.TestingSessionLocal()
        model = db.query(Todos).filter(Todos.id == 1).first()
        assert model.title == "New Todo2"
        assert model.description == "some description"
        assert model.priority == 4
        assert model.completed
        db.close()


async def test_delete_todo_not_found(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.delete("http://127.0.0.1:8000/todos/1000/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_delete_todo(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.delete("http://127.0.0.1:8000/todos/1/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        db = utils.TestingSessionLocal()
        model = db.query(Todos).filter(Todos.id == 1).first()
        assert model is None
        db.close()
