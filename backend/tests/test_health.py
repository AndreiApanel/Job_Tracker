import pytest
from app.db.session import get_db
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


class BrokenSession:
    async def execute(self, *args, **kwargs):
        raise OSError("connection refused")


@pytest.fixture
def broken_db():
    async def override():
        yield BrokenSession()

    app.dependency_overrides[get_db] = override
    yield
    app.dependency_overrides.clear()


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_db_unavailable(broken_db):
    response = client.get("/health/db")
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    assert "refused" not in response.text
