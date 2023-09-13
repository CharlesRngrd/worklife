from uuid import uuid4

from fastapi import HTTPException, status

from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def _query(self, session: Session, *_, **kwargs) -> Query:
        filters = [getattr(self.model, k) == v for k, v in kwargs.items()]
        objs: Query = session.query(self.model).filter(*filters)

        if not objs.count():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        return objs

    def _base_to_model(self, obj, obj_in):
        for column in self.model.__table__.columns.keys():
            if column != "id":
                setattr(obj, column, getattr(obj_in, column))

    def get(self, session, *_, **kwargs):
        return self._query(session, **kwargs).one()

    def get_many(self, session: Session, *_, **kwargs):
        return self._query(session, **kwargs).all()

    def create(self, session: Session, obj_in):
        obj = self.model()
        obj.id = uuid4()
        self._base_to_model(obj, obj_in)

        session.add(obj)
        session.commit()
        return obj

    def update(self, session: Session, id, obj_in):
        obj = self.get(session, id=id)
        self._base_to_model(obj, obj_in)

        session.commit()
        return obj

    def delete(self, session: Session, id):
        obj = self.get(session, id=id)
        session.delete(obj)
        session.commit()
        return obj
