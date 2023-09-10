import sqlalchemy as sa

from .base import BaseModel


class EmployeeModel(BaseModel):
    __tablename__ = "employee"
    first_name = sa.Column(sa.String, nullable=False)
    last_name = sa.Column(sa.String, nullable=False)
