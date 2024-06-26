from fastapi import status
from httpx import AsyncClient
from ..main import app
from ..models import Todos
from ..routers.admin import get_db, get_current_user
from . import utils


app.dependency_overrides[get_db] = utils.override_get_db
app.dependency_overrides[get_current_user] = utils.override_get_current_user


async def test_admin_read_all_authenticated(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.get("http://127.0.0.1:8000/admin/todo/")
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


async def test_admin_delete_todo(test_todo):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.delete("http://127.0.0.1:8000/admin/todo/1/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        db = utils.TestingSessionLocal()
        model = db.query(Todos).filter(Todos.id == 1).first()
        assert model is None
        db.close()


async def test_admin_delete_todo_not_fount():
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.delete("http://127.0.0.1:8000/admin/todo/10000/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "item not found."}
