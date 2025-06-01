from fastapi import APIRouter

from app.api.v0.auth import router as AuthRouter
from app.api.v0.transactions import router as TransactionRouter
from app.api.v0.accounts import router as AccountRouter

router = APIRouter(prefix="/v0")

router.include_router(AuthRouter)
router.include_router(TransactionRouter)
router.include_router(AccountRouter)
