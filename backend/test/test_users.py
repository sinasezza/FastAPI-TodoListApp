from fastapi import status
from httpx import AsyncClient

from ..main import app
from ..models import Users
from ..routers.auth import bcrypt_context
from ..routers.users import get_current_user, get_db
from . import utils

app.dependency_overrides[get_db] = utils.override_get_db
app.dependency_overrides[get_current_user] = utils.override_get_current_user


async def test_return_user(test_user):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.get("http://127.0.0.1:8000/users/info/")
        assert response.status_code == status.HTTP_200_OK
        res = response.json()
        assert res["id"] == 1
        assert res["username"] == "testuser"
        # assert res["hashed_password"] == bcrypt_context.hash("testpass")
        assert res["email"] == "testemail@test.com"
        assert res["phone_number"] == "1234567890"
        assert res["role"] == "admin"


async def test_change_password_success(test_user):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.post(
            "http://127.0.0.1:8000/users/change-pass/",
            json={"password": "testpass", "new_password": "123456"},
        )
        assert response.status_code == status.HTTP_202_ACCEPTED


async def test_change_password_success_failure(test_user):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.post(
            "http://127.0.0.1:8000/users/change-pass/",
            json={"password": "testpasssss", "new_password": "123456"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Error on password Change."}


async def test_change_phone_number_success(test_user):
    async with AsyncClient(transport=utils.transport) as client:
        response = await client.put(
            "http://127.0.0.1:8000/users/change-phone-number/",
            json={"phone_number": "1234567890"},
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
