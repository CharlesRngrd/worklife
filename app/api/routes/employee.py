from typing import Optional
from uuid import UUID

from app.db.session import get_db
from app.repository.employee import EmployeeRepository
from app.schema import EmployeeBase, EmployeeBaseNoId

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=Optional[EmployeeBase])
def create_employee(session: Session = Depends(get_db), *, employee: EmployeeBaseNoId):
    return EmployeeRepository.create(session=session, obj_in=employee)


@router.get("/all", response_model=Optional[list[EmployeeBase]])
def get_employees(session: Session = Depends(get_db)):
    return EmployeeRepository.get_many(session=session)


@router.get("/{employee_id}", response_model=Optional[EmployeeBase])
def get_employee(session: Session = Depends(get_db), *, employee_id: UUID):
    return EmployeeRepository.get(session=session, id=employee_id)


@router.put("/{employee_id}", response_model=Optional[EmployeeBase])
def put_employee(
    session: Session = Depends(get_db), *, employee_id: UUID, employee: EmployeeBaseNoId
):
    return EmployeeRepository.update(session=session, id=employee_id, obj_in=employee)


@router.delete("/{employee_id}", response_model=Optional[EmployeeBase])
def delete_employee(session: Session = Depends(get_db), *, employee_id: UUID):
    return EmployeeRepository.delete(session=session, id=employee_id)
