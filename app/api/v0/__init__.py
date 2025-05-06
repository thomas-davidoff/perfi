from fastapi import APIRouter

from app.api.v0.auth import router as AuthRouter

router = APIRouter(prefix="/v0")

router.include_router(AuthRouter)
