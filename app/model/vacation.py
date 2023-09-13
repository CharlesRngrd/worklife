from enum import Enum

import sqlalchemy as sa

from .base import BaseModel, CustomUUID
from .employee import EmployeeModel


class VacationTypes(Enum):
    PAID = "paid"
    UNPAID = "unpaid"


class VacationModel(BaseModel):
    __tablename__ = "vacation"
    employee_id = sa.Column(
        CustomUUID(as_uuid=True), sa.ForeignKey(EmployeeModel.id, ondelete="CASCADE")
    )
    type = sa.Column(sa.Enum(VacationTypes), nullable=False)
    date_start = sa.Column(sa.Date, nullable=False)
    date_end = sa.Column(sa.Date, nullable=False)
