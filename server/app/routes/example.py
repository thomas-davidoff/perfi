from fastapi import APIRouter

router = APIRouter()


@router.get("/example")
async def example_route():
    return {"message": "This is an example route"}
