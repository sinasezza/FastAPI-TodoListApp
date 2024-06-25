import pytest
from fastapi import status
from httpx import AsyncClient
from httpx import ASGITransport
from ..main import app

transport = ASGITransport(app=app)

@pytest.mark.asyncio
async def test_return_health_check():
    async with AsyncClient(transport=transport) as client:
        response = await client.get("http://127.0.0.1:8000/healthy/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
