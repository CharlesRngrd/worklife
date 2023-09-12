from functools import wraps

import pytest

from .setup import setup_environment

client = setup_environment()


class TestEmployee:
    @pytest.fixture
    def employees(self):
        return (
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
        )

    @pytest.fixture
    def wrong_employees(self):
        return (
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
        )

    # TODO: Switch this to a decorator.
    def insert_employees(self, employees):
        return [client.post("/employee", json=employee).json() for employee in employees]

    def delete_employees(function):
        @wraps(function)
        def wrag_function(*args, **kwargs):
            response = client.get("/employee/all")
            if response.status_code == 200:
                for employee in response.json():
                    client.delete(f"/employee/{employee['id']}")
            function(*args, **kwargs)

        return wrag_function

    @delete_employees
    def test_wrong_route_parameter(self, employees):
        """It should return 404 if employee doesn't exist."""
        wrong_uuid = "f7833f1e-5537-4080-87e9-0efcff339308"

        responses = (
            client.get("/employee/all"),
            client.get(f"/employee/{wrong_uuid}"),
            client.delete(f"/employee/{wrong_uuid}"),
            client.put(f"/employee/{wrong_uuid}", json=employees[0]),
        )

        for response in responses:
            assert response.status_code == 404
            assert response.json()["detail"] == "Item not found"

    @delete_employees
    def test_create_employee(self, employees):
        """It should create an employee."""
        for index, employee in enumerate(employees):
            response = client.post("/employee", json=employee)

            assert response.status_code == 200
            assert response.json()["id"]

            employee["id"] = response.json()["id"]

            for key in ("first_name", "last_name"):
                assert response.json()[key] == employees[index][key]

    @delete_employees
    def test_get_employees(self, employees):
        """It should retrieve all the employees."""
        employees = self.insert_employees(employees)

        response = client.get("/employee/all")

        assert response.status_code == 200
        assert response.json() == employees

    @delete_employees
    def test_get_employee(self, employees):
        """It should retrieve a single employee."""
        employees = self.insert_employees(employees)

        for employe in employees:
            response = client.get(f"/employee/{employe['id']}")

            assert response.status_code == 200
            assert response.json() == employe

    @delete_employees
    def test_update_employee(self, employees):
        """It should update an employee."""
        employees = self.insert_employees(employees)

        employees[0]["first_name"] += "_updated"
        employee_json = employees[0].copy()
        employee_json.pop("id")

        response = client.put(f"/employee/{employees[0]['id']}", json=employee_json)

        assert response.status_code == 200
        assert response.json() == employees[0]

    @delete_employees
    def test_delete_employee(self, employees):
        """It should delete an employee."""
        employees = self.insert_employees(employees)

        for employe in employees:
            response = client.get(f"/employee/{employe['id']}")
            assert response.status_code == 200

            client.delete(f"/employee/{employe['id']}")
            assert response.status_code == 200

            response = client.get(f"/employee/{employe['id']}")
            assert response.status_code == 404

    @delete_employees
    def test_wrong_data(self, wrong_employees):
        """It should not create an employee with wrong input."""
        for employee in wrong_employees:
            response = client.post("/employee", json=employee)

            assert response.status_code == 422
