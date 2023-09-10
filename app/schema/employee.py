from app.model.employee import EmployeeModel

from fastapi import status

from pydantic_sqlalchemy import sqlalchemy_to_pydantic


class EmployeeBase(sqlalchemy_to_pydantic(EmployeeModel)):
    ...


class EmployeeBaseNoId(sqlalchemy_to_pydantic(EmployeeModel, exclude=["id"])):
    def __init__(self, *_, **kwargs):
        super().__init__(*_, **kwargs)
        if "id" in kwargs:
            raise status.HTTP_422_UNPROCESSABLE_ENTITY()
