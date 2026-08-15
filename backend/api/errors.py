from fastapi import APIRouter

router = APIRouter()


@router.get("/404-test")
def test_error():
    raise Exception("This is a test exception.")