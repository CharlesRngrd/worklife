from datetime import date
from typing import Optional
from uuid import UUID

from app.db.session import get_db
from app.model.vacation import VacationTypes
from app.repository.vacation import VacationRepository
from app.schema import VacationBase, VacationBaseNoId

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/", response_model=Optional[VacationBase])
def create_vacation(session: Session = Depends(get_db), *, vacation: VacationBaseNoId):
    return VacationRepository.create(session=session, obj_in=vacation)


@router.get("/all", response_model=Optional[list[VacationBase]])
def get_vacations(
    session: Session = Depends(get_db), type: VacationTypes | None = None, date: date | None = None
):
    filters = {}
    if type:
        filters["type"] = type

    return VacationRepository.get_many(session=session, date=date, **filters)


@router.get("/{vacation_id}", response_model=Optional[VacationBase])
def get_vacation(session: Session = Depends(get_db), *, vacation_id: UUID):
    return VacationRepository.get(session=session, id=vacation_id)


@router.put("/{vacation_id}", response_model=Optional[VacationBase])
def put_vacation(
    session: Session = Depends(get_db), *, vacation_id: UUID, vacation: VacationBaseNoId
):
    return VacationRepository.update(session=session, id=vacation_id, obj_in=vacation)


@router.delete("/{vacation_id}", response_model=Optional[VacationBase])
def delete_vacation(session: Session = Depends(get_db), *, vacation_id: UUID):
    return VacationRepository.delete(session=session, id=vacation_id)
