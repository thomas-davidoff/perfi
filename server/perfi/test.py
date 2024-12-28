from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from perfi.core.repositories import UserRepository
from fastapi import APIRouter
from uuid import UUID, uuid4
from perfi.core.dependencies.session import get_async_session


router = APIRouter()


async def some_service(id: int, session: AsyncSession = Depends(get_async_session)):
    return await UserRepository().get_by_id(session, id)


example_id = UUID("51480452-d147-4194-b61e-3f033fdbbcc9")


@router.get("/create")
async def example_route2(session: AsyncSession = Depends(get_async_session)):

    await UserRepository().create(
        session=session,
        data={
            "email": "poop@poop.com",
            "password": "123adjna9sdC",
            "username": "thomas",
        },
    )

    user = await UserRepository().get_by_username_or_email(
        session=session, username_or_email="thomas"
    )


@router.get("/test")
async def example_route(
    id: UUID = example_id, session: AsyncSession = Depends(get_async_session)
):

    user = await some_service(id=id, session=session)
    return {"message": f"User found: {user}"}
