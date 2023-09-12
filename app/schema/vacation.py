from datetime import date, timedelta

from app.model.vacation import VacationModel

from fastapi import HTTPException

from pydantic import root_validator

from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from .base import NoId


class VacationBase(sqlalchemy_to_pydantic(VacationModel)):
    @staticmethod
    def _get_last_business_day(date: date) -> date:
        while date.weekday() >= 5:
            date -= timedelta(days=1)

        return date

    @staticmethod
    def _get_next_business_day(date: date) -> date:
        while date.weekday() >= 5:
            date += timedelta(days=1)

        return date

    @staticmethod
    def _compute_duration(date_start: date, date_end: date) -> int:
        return (date_end - date_start).days

    @staticmethod
    def _check_duration(duration):
        if duration < 1:
            raise HTTPException(status_code=422, detail="Start date should be before end date")

    @root_validator
    def validate_vacation(cls, values):
        values["date_start"] = cls._get_next_business_day(values["date_start"])
        values["date_end"] = cls._get_last_business_day(values["date_end"])
        values["duration"] = cls._compute_duration(values["date_start"], values["date_end"])

        cls._check_duration(values["duration"])

        return values


class VacationBaseNoId(NoId, sqlalchemy_to_pydantic(VacationModel, exclude=["id"])):
    ...
