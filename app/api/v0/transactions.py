from app.schemas.transaction import TransactionCreateSchema, TransactionSchema
from fastapi import Depends, status, APIRouter
from db.session_manager import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v0.schema import ApiResponse


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    transaction_data: TransactionCreateSchema,
    session: AsyncSession = Depends(get_session),
):
    pass
