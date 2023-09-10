from app.api import add_app_routes
from app.db.session import get_db
from app.main import app
from app.model.employee import EmployeeModel

from fastapi.testclient import TestClient

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# TODO: Use a test DB for testing.
engine = create_engine(
    "postgresql://dev:dev@worklife-test-db:5432/dev",
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

EmployeeModel.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

add_app_routes(app)

client = TestClient(app)


class TestEmployee:
    @pytest.fixture
    def employees(self):
        return [
            {
                "first_name": "Bill",
                "last_name": "XXX",
            },
            {
                "first_name": "Bob",
                "last_name": "XXX",
            },
            {
                "first_name": "Brad",
                "last_name": "XXX",
            },
        ]

    @pytest.fixture
    def wrong_employees(self):
        return [
            # Missing "first_name".
            {
                "last_name": "XXX",
            },
            # Missing "last_name".
            {
                "first_name": "Bob",
            },
            # Unexpected "id".
            {
                "id": "f7833f1e-5537-4080-87e9-0efcff339308",
                "first_name": "Brad",
                "last_name": "XXX",
            },
        ]

    def test_wrong_route_parameter(self, employees):
        wrong_uuid = "f7833f1e-5537-4080-87e9-0efcff339308"

        responses = [
            client.get("/employee/all"),
            client.get(f"/employee/{wrong_uuid}"),
            client.delete(f"/employee/{wrong_uuid}"),
            client.put(f"/employee/{wrong_uuid}", json=employees[0]),
        ]

        for response in responses:
            assert response.status_code == 404
            assert response.json()["detail"] == "Item not found"

    def test_employee(self, employees):
        self._test_create_employee(employees)
        self._test_get_employees(employees)
        self._test_get_employee(employees)
        self._test_update_employee(employees)
        self._test_delete_employee(employees)

    def _test_create_employee(self, employees):
        for index, employee in enumerate(employees):
            response = client.post("/employee", json=employee)

            assert response.status_code == 200
            assert response.json()["id"]

            employee["id"] = response.json()["id"]

            for key in ("first_name", "last_name"):
                assert response.json()[key] == employees[index][key]

    def _test_get_employees(self, employees):
        response = client.get("/employee/all")

        assert response.status_code == 200
        assert response.json() == employees

    def _test_get_employee(self, employees):
        for employe in employees:
            response = client.get(f"/employee/{employe['id']}")

            assert response.status_code == 200
            assert response.json() == employe

    def _test_update_employee(self, employees):
        employee = client.get(f"/employee/{employees[0]['id']}").json()

        employee["first_name"] += "_updated"
        employee_json = employee.copy()
        employee_json.pop("id")

        response = client.put(f"/employee/{employees[0]['id']}", json=employee_json)

        assert response.status_code == 200
        assert response.json() == employee

    def _test_delete_employee(self, employees):
        for employe in employees:
            response = client.get(f"/employee/{employe['id']}")
            assert response.status_code == 200

            client.delete(f"/employee/{employe['id']}")
            assert response.status_code == 200

            response = client.get(f"/employee/{employe['id']}")
            assert response.status_code == 404

    def test_wrong_data(self, wrong_employees):
        for employee in wrong_employees:
            response = client.post("/employee", json=employee)

            assert response.status_code == 422
