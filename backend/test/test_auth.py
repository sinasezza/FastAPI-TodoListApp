from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException, status
from httpx import AsyncClient
from jose import jwt

from ..main import app
from ..models import Users
from ..routers import auth
from ..routers.auth import get_current_user, get_db
from . import utils

app.dependency_overrides[get_db] = utils.override_get_db
app.dependency_overrides[get_current_user] = utils.override_get_current_user


async def test_authenticate_user(test_user):
    db = utils.TestingSessionLocal()

    authenticated_user = await auth.authenticate_user(
        test_user.username, "testpass", db
    )

    assert authenticated_user is not False
    assert authenticated_user.username == test_user.username

    wrong_user = await auth.authenticate_user("wronguser", "testpass", db)
    assert wrong_user is False

    false_pass_user = await auth.authenticate_user(test_user.username, "wrongpass", db)
    assert false_pass_user is False


async def test_create_access_token():
    username = "testuser"
    user_id = 1
    role = "admin"
    expires_delta = timedelta(minutes=15)
    access_token = auth.create_access_token(username, user_id, role, expires_delta)
    assert access_token

    decoded_token = jwt.decode(
        access_token,
        auth.SECRET_KEY,
        algorithms=[auth.ALGORITHM],
        options={"verify_signature": False},
    )
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role


async def test_get_current_user_valid_token():
    encode = {"sub": "testuser", "id": 1, "role": "admin"}
    token = jwt.encode(encode, auth.SECRET_KEY, auth.ALGORITHM)

    user = await auth.get_current_user(token)
    assert user == {"username": "testuser", "id": 1, "user_role": "admin"}


async def test_get_current_user_missing_payload():
    encode = {"role": "user"}
    token = jwt.encode(encode, auth.SECRET_KEY, auth.ALGORITHM)

    with pytest.raises(HTTPException) as e:
        await auth.get_current_user(token)
    assert e.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert e.value.detail == "Could not validate credentials"
