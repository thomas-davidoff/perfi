from database import User
from extensions import jwt
from .user import create_user_service, UserService
from app.exceptions import MissingRegistrationData


@jwt.user_identity_loader
def user_identity_lookup(user: User):
    """
    Callback function uses when creating access tokens with `jwt.create_access_token`

    :param user:
        The identity (SQLAlchemy User object) that is passed into create_access_token.

    :return:
        The id of the user object
    """
    return user.id


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


class AuthService:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    def authenticate(self, username_or_email, password) -> User:
        user = self.user_service.get_by_username_or_email(str(username_or_email))
        if user and user.verify_password(str(password)):
            return user

    def register_user(self, username, email, password) -> User:

        if any([required is None for required in [username, email, password]]):
            raise MissingRegistrationData

        return self.user_service.create_user(
            username=str(username), email=str(email), password=str(password)
        )


def create_auth_service():
    user_service = create_user_service()
    return AuthService(user_service)
