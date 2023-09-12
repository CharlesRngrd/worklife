from fastapi import HTTPException


# TODO: Investigate why "sqlalchemy_to_pydantic" do not the following validation.
class NoId:
    def __init__(self, *_, **kwargs):
        super().__init__(*_, **kwargs)
        if "id" in kwargs:
            raise HTTPException(
                status_code=422, detail="Id is created on the fly, cannot be set or modified"
            )
