from .auth import router as auth_router
from .top import router as top_router
from .transaction import router as transactions_router
from .account import router as account_router
from .file_import import router as file_import_router


routers = [
    top_router,
    auth_router,
    transactions_router,
    account_router,
    file_import_router,
]
