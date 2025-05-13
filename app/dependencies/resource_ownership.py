from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar
from app.models import Account, User
from app.dependencies.auth import get_current_active_user
from db.session_manager import get_session
from app.services.accounts import AccountRepository
from app.exc import NotFoundException, AuthorizationException
import logging

logger = logging.getLogger(__name__)
from fastapi import Depends

T = TypeVar("T")

from fastapi import Depends


def get_owned_account_for(model_cls, field_name: str = "account_id"):
    """Generate a properly-typed dependency function for a specific model type."""

    async def verify_account_ownership(
        transaction_data: model_cls,  # type: ignore
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_session),
    ) -> Account:
        """Verify that the user owns the account specified in the transaction request."""
        account = await AccountRepository.get_one_by_id(
            session, getattr(transaction_data, field_name)
        )

        if not account:
            raise NotFoundException("Account not found")

        if account.user_id != current_user.uuid:
            logger.warning("Unauthorized access attempted")
            raise AuthorizationException("You do not have access to this resource.")

        return account

    return verify_account_ownership
