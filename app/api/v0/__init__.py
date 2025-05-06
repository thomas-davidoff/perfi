from fastapi import APIRouter

from app.api.v0.auth import router as AuthRouter
from app.api.v0.transactions import router as TransactionRouter

router = APIRouter(prefix="/v0")

router.include_router(AuthRouter)
router.include_router(TransactionRouter)
