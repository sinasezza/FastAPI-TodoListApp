import pytest
from fastapi import status
from httpx import AsyncClient
from httpx import ASGITransport
import main

transport = ASGITransport(app=main.app)

@pytest.mark.asyncio
async def test_return_health_check():
    async with AsyncClient(transport=transport) as client:
        response = await client.get("http://127.0.0.1:8000/healthy/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
