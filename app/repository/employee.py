from app.model import EmployeeModel
from app.repository.base import BaseRepository


class _EmployeeRepository(BaseRepository):
    ...


EmployeeRepository = _EmployeeRepository(model=EmployeeModel)
