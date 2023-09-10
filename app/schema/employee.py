from app.model.employee import EmployeeModel

from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from .base import NoId


class EmployeeBase(sqlalchemy_to_pydantic(EmployeeModel)):
    ...


class EmployeeBaseNoId(NoId, sqlalchemy_to_pydantic(EmployeeModel, exclude=["id"])):
    ...
