from app.api import add_app_routes
from app.main import app

from fastapi.testclient import TestClient

add_app_routes(app)

client = TestClient(app)


def test_get_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"msg": "OK"}
