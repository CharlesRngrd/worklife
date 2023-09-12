from app.model import EmployeeModel
from app.repository.base import BaseRepository

from fastapi import HTTPException

from sqlalchemy.orm.session import Session


class _EmployeeRepository(BaseRepository):
    def check_employee_exists(self, session: Session, employee_id):
        employee = session.query(self.model).filter(self.model.id == employee_id).count()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee doesn't exist")


EmployeeRepository = _EmployeeRepository(model=EmployeeModel)
