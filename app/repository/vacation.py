from app.model import VacationModel
from app.repository.base import BaseRepository
from app.repository.employee import EmployeeRepository

from fastapi import HTTPException

import sqlalchemy as sa
from sqlalchemy.orm.session import Session


class VacationMerge:
    @staticmethod
    def check_overlaps(model, session: Session, obj_in):
        # Step 1: Define overlap filters.
        condition_overlap = sa.or_(
            model.date_start.between(obj_in.date_start, obj_in.date_end),
            model.date_end.between(obj_in.date_start, obj_in.date_end),
        ).self_group()

        # Step 2: Query overlaps.
        overlaps = session.query(model).filter(
            sa.and_(condition_overlap, model.employee_id == obj_in.employee_id)
        )

        # Step 3: Check overlap errors.
        if overlaps and any([overlap.type != obj_in.type for overlap in overlaps]):
            raise HTTPException(
                status_code=422, detail="Vacation overlaps cannot be merged if types are different"
            )

        # Step 4: Return overlaps that can be merged.
        return overlaps

    @staticmethod
    def set_vacation_dates(overlaps, obj_in):
        dates_start = [overlap.date_start for overlap in overlaps]
        dates_start.append(obj_in.date_start)
        obj_in.date_start = min(dates_start)

        dates_end = [overlap.date_end for overlap in overlaps]
        dates_end.append(obj_in.date_end)
        obj_in.date_end = max(dates_end)

    @staticmethod
    def drop_overlaps(session, overlaps):
        for overlap in overlaps:
            session.delete(overlap)
        session.commit()


class _VacationRepository(BaseRepository):
    def create(self, session, obj_in):
        # Step 1: Check employee exists.
        EmployeeRepository.check_employee_exists(session, obj_in.employee_id)

        # Step 2: Check if overlaps.
        overlaps = VacationMerge.check_overlaps(self.model, session, obj_in).all()

        # Step 3: Delete the overlap vacations + prepare the new dates for the merge.
        if overlaps:
            VacationMerge.drop_overlaps(session, overlaps)
            VacationMerge.set_vacation_dates(overlaps, obj_in)

        # Step 4: Create the merge.
        return super().create(session=session, obj_in=obj_in)

    # NOTE: Does it make sense to update the employee ? If not add a check on it.
    def update(self, session, id, obj_in):
        # Step 0: Retrieve the updated vacation.
        update_filter = None
        vacation = self.get(session, id=id)
        if vacation:
            update_filter = self.model.id != id

        # Step 1: Check employee exists.
        EmployeeRepository.check_employee_exists(session, obj_in.employee_id)

        # Step 2: Check if overlaps.
        overlaps = (
            VacationMerge.check_overlaps(self.model, session, obj_in).filter(update_filter).all()
        )

        # Step 3: Delete the overlap vacations + prepare the new dates for the merge.
        if overlaps:
            # Must delete the vacation to be updated.
            VacationMerge.drop_overlaps(session, overlaps + [vacation])
            VacationMerge.set_vacation_dates(overlaps, obj_in)

            # Step 4 (option A): Create the merge.
            return super().create(session=session, obj_in=obj_in)

        # Step 4 (option B): Update the vacation.
        return super().update(session=session, id=id, obj_in=obj_in)

    def get_many(self, session: Session, date, *_, **kwargs):
        filter = []
        if date:
            filter = [sa.and_(self.model.date_start <= date, self.model.date_end >= date)]
        return self._query(session, **kwargs).filter(*filter).all()


VacationRepository = _VacationRepository(model=VacationModel)
