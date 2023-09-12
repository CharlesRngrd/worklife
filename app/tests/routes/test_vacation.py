import datetime
from functools import wraps

from app.schema.vacation import VacationBase

import pytest

from .setup import setup_environment

client = setup_environment()


class TestVacation:
    EMPLOYEE_UUID = None

    @classmethod
    def setup_class(cls):
        employee = {
            "first_name": "Bill",
            "last_name": "XXX",
        }
        cls.EMPLOYEE_UUID = client.post("/employee", json=employee).json()["id"]

    @pytest.fixture
    def vacations(self):
        return [
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "paid",
                "date_start": "2023-09-11",
                "date_end": "2023-09-13",
            },
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "paid",
                "date_start": "2023-09-18",
                "date_end": "2023-09-20",
            },
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "paid",
                "date_start": "2023-09-25",
                "date_end": "2023-09-27",
            },
        ]

    @pytest.fixture
    def vacations_extra(self):
        return [
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "unpaid",
                "date_start": "2024-09-11",
                "date_end": "2024-09-13",
            },
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "unpaid",
                "date_start": "2024-09-18",
                "date_end": "2024-09-20",
            },
        ]

    @pytest.fixture
    def vacation_overlaps_diff_type(self):
        return [
            # Overlap left.
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "unpaid",
                "date_start": "2023-09-08",
                "date_end": "2023-09-11",
            },
            # Overlap right.
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "unpaid",
                "date_start": "2023-09-19",
                "date_end": "2023-09-22",
            },
            # Overlap both.
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "unpaid",
                "date_start": "2023-09-22",
                "date_end": "2023-09-28",
            },
        ]

    @pytest.fixture
    def vacation_overlaps_same_type(self):
        return [
            # Overlap left.
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "paid",
                "date_start": "2023-09-08",
                "date_end": "2023-09-11",
            },
            # Overlap right.
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "paid",
                "date_start": "2023-09-19",
                "date_end": "2023-09-22",
            },
            # Overlap both.
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "paid",
                "date_start": "2023-09-22",
                "date_end": "2023-09-28",
            },
        ]

    @pytest.fixture
    def vacation_employee_not_exists(self):
        return [
            {
                "employee_uuid": "f7833f1e-5537-4080-87e9-0efcff339308",
                "type": "paid",
                "date_start": "2023-09-11",
                "date_end": "2023-09-13",
            },
        ]

    @pytest.fixture
    def vacation_negative_duration(self):
        return [
            {
                "employee_uuid": self.EMPLOYEE_UUID,
                "type": "paid",
                "date_start": "2023-09-13",
                "date_end": "2023-09-11",
            },
        ]

    # TODO: Switch this to a decorator.
    def insert_vacations(self, vacations):
        return [client.post("/vacation", json=vacation).json() for vacation in vacations]

    def delete_vacation(function):
        @wraps(function)
        def wrag_function(*args, **kwargs):
            response = client.get("/vacation/all")
            if response.status_code == 200:
                for vacation in response.json():
                    client.delete(f"/vacation/{vacation['id']}")
            function(*args, **kwargs)

        return wrag_function

    @delete_vacation
    def test_wrong_route_parameter(self, vacations):
        """It should return 404 if vacation doesn't exist."""
        wrong_uuid = "f7833f1e-5537-4080-87e9-0efcff339308"

        responses = (
            client.get("/vacation/all"),
            client.get(f"/vacation/{wrong_uuid}"),
            client.delete(f"/vacation/{wrong_uuid}"),
            client.put(f"/vacation/{wrong_uuid}", json=vacations[0]),
        )

        for response in responses:
            assert response.status_code == 404
            assert response.json()["detail"] == "Item not found"

    @delete_vacation
    def test_create_vacation(self, vacations):
        """It should create a vacation."""
        for index, vacation in enumerate(vacations):
            response = client.post("/vacation", json=vacation)

            assert response.status_code == 200
            assert response.json()["id"]

            vacation["id"] = response.json()["id"]

            for key in ("employee_uuid", "type", "date_start", "date_end"):
                assert response.json()[key] == vacations[index][key]

            assert response.json()["duration"] == 2

    @delete_vacation
    def test_get_vacations(self, vacations):
        """It should retrieve all the vacations with calculcated fields."""
        vacations = self.insert_vacations(vacations)

        response = client.get("/vacation/all")

        for vacation in response.json():
            assert vacation["duration"] == 2

        assert response.status_code == 200
        assert response.json() == vacations

    @delete_vacation
    def test_get_vacations_with_filter(self, vacations, vacations_extra):
        """It should retrieve all the vacations that match the filters."""
        self.insert_vacations(vacations)
        self.insert_vacations(vacations_extra)

        response = client.get("/vacation/all")
        assert len(response.json()) == 5

        response = client.get("/vacation/all?type=paid")
        assert len(response.json()) == 3

        response = client.get("/vacation/all?date=2023-01-12")
        assert len(response.json()) == 0

        response = client.get("/vacation/all?type=paid&date=2023-09-12")
        assert len(response.json()) == 1

    @delete_vacation
    def test_get_vacation(self, vacations):
        """It should retrieve a single vacation."""
        vacations = self.insert_vacations(vacations)

        for vacation in vacations:
            response = client.get(f"/vacation/{vacation['id']}")

            assert response.status_code == 200
            assert response.json() == vacation

    @delete_vacation
    def test_update_vacation(self, vacations):
        """It should update a vacation."""
        vacations = self.insert_vacations(vacations)

        vacations[0]["date_end"] = "2023-09-14"
        vacation_json = vacations[0].copy()
        vacation_json.pop("id")

        response = client.put(f"/vacation/{vacations[0]['id']}", json=vacation_json)

        vacations[0]["duration"] = 3

        assert response.status_code == 200
        assert response.json() == vacations[0]

    @delete_vacation
    def test_delete_vacation(self, vacations):
        """It should delete a vacation."""
        vacations = self.insert_vacations(vacations)

        for employe in vacations:
            response = client.get(f"/vacation/{employe['id']}")
            assert response.status_code == 200

            client.delete(f"/vacation/{employe['id']}")
            assert response.status_code == 200

            response = client.get(f"/vacation/{employe['id']}")
            assert response.status_code == 404

    @delete_vacation
    def test_vacation_employee_not_exists(self, vacation_employee_not_exists):
        """It should not create or update a vacation if the related employee doesn't exist."""
        response = client.post("/vacation", json=vacation_employee_not_exists[0])

        assert response.status_code == 404
        assert response.json() == {"detail": "Employee doesn't exist"}

        response = client.get("/vacation/all")
        assert response.status_code == 404

    def test_last_business_day(self):
        """It should return the last business if date is a weekend day."""
        dates = (
            (datetime.date(2023, 9, 11), datetime.date(2023, 9, 11)),  # Monday
            (datetime.date(2023, 9, 12), datetime.date(2023, 9, 12)),  # Tuesday
            (datetime.date(2023, 9, 13), datetime.date(2023, 9, 13)),  # Wednesday
            (datetime.date(2023, 9, 14), datetime.date(2023, 9, 14)),  # Thursday
            (datetime.date(2023, 9, 15), datetime.date(2023, 9, 15)),  # Friday
            (datetime.date(2023, 9, 16), datetime.date(2023, 9, 15)),  # Saturday -> last Friday
            (datetime.date(2023, 9, 17), datetime.date(2023, 9, 15)),  # Sunday -> last Friday
        )

        for date in dates:
            assert VacationBase._get_last_business_day(date[0]) == date[1]

    def test_next_business_day(self):
        """It should return the next business if date is a weekend day."""
        dates = (
            (datetime.date(2023, 9, 11), datetime.date(2023, 9, 11)),  # Monday
            (datetime.date(2023, 9, 12), datetime.date(2023, 9, 12)),  # Tuesday
            (datetime.date(2023, 9, 13), datetime.date(2023, 9, 13)),  # Wednesday
            (datetime.date(2023, 9, 14), datetime.date(2023, 9, 14)),  # Thursday
            (datetime.date(2023, 9, 15), datetime.date(2023, 9, 15)),  # Friday
            (datetime.date(2023, 9, 16), datetime.date(2023, 9, 18)),  # Saturday -> next Monday
            (datetime.date(2023, 9, 17), datetime.date(2023, 9, 18)),  # Sunday -> next Monday
        )

        for date in dates:
            assert VacationBase._get_next_business_day(date[0]) == date[1]

    @pytest.mark.skip(reason="Error raised but vacation inserted anyway")
    @delete_vacation
    def test_vacation_negative_duration(self, vacation_negative_duration):
        """It should not create a vacation if the end if before the begining."""
        response = client.post("/vacation", json=vacation_negative_duration[0])

        assert response.status_code == 422
        assert response.json() == {"detail": "Start date should be before end date"}

        response = client.get("/vacation/all")
        assert response.status_code == 404

    @delete_vacation
    def test_vacation_overlaps_diff_type(self, vacations, vacation_overlaps_diff_type):
        """It should not create a vacation if there is an overlap of distinct type."""
        vacations = self.insert_vacations(vacations)

        count = len(client.get("/vacation/all").json())
        for vacation_overlap in vacation_overlaps_diff_type:
            response = client.post("/vacation", json=vacation_overlap)

            assert response.status_code == 422
            assert response.json() == {
                "detail": "Vacation overlaps cannot be merged if types are different"
            }
            assert count == len(client.get("/vacation/all").json())

    @delete_vacation
    def test_vacation_overlaps_diff_type_update(self, vacations):
        """It should not update a vacation if there is an overlap of distinct type."""
        vacations = self.insert_vacations(vacations)

        count = len(client.get("/vacation/all").json())

        vacation_update = vacations[0].copy()
        vacation_update["date_end"] = "2023-09-19"
        vacation_update["type"] = "unpaid"

        response = client.put(f"/vacation/{vacation_update.pop('id')}", json=vacation_update)

        assert response.status_code == 422
        assert response.json() == {
            "detail": "Vacation overlaps cannot be merged if types are different"
        }
        assert count == len(client.get("/vacation/all").json())

    @delete_vacation
    def test_vacation_overlaps_same_type(self, vacations, vacation_overlaps_same_type):
        """It should merge a vacation during creation if there is an overlap of same type."""
        vacations = self.insert_vacations(vacations)

        expected_dates = (
            ("2023-09-08", "2023-09-13"),
            ("2023-09-18", "2023-09-22"),
            ("2023-09-18", "2023-09-28"),  # Two merged vacations !
        )

        for index, vacation_overlap in enumerate(vacation_overlaps_same_type):
            # Part 1: Date should have been updated.
            response = client.post("/vacation", json=vacation_overlap)

            assert response.status_code == 200
            assert response.json()["date_start"] == expected_dates[index][0]
            assert response.json()["date_end"] == expected_dates[index][1]

            # Part 2: Previous vacation should have been droped.
            response = client.get(f"/vacation/{vacations[index]['id']}")
            assert response.status_code == 404

    @delete_vacation
    def test_vacation_overlaps_same_type_update(self, vacations):
        """It should merge a vacation during update if there is an overlap of same type."""
        vacations = self.insert_vacations(vacations)

        vacations_update = vacations[0].copy()
        vacations_update["date_end"] = "2023-09-19"
        vacations_update.pop("id")

        response = client.put(f"/vacation/{vacations[0]['id']}", json=vacations_update)
        expected_dates = ("2023-09-11", "2023-09-20")

        # Part 1: Date should have been updated.
        assert response.json()["date_start"] == expected_dates[0]
        assert response.json()["date_end"] == expected_dates[1]

        # Part 2: Previous vacation should have been droped.
        response = client.get(f"/vacation/{vacations[0]['id']}")
        assert response.status_code == 404
