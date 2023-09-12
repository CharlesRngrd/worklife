from fastapi import APIRouter

router = APIRouter()


@router.get("")
def ping():
    return {"msg": "OK"}
