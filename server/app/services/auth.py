from database import User
from extensions import jwt
from app.repositories import UserRepository


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
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repo = user_repository

    def authenticate(self, username_or_email, password) -> User:
        user = self.user_repo.get_by_username_or_email(username_or_email)
        if user and user.verify_password(password):
            return user


def create_auth_service():
    user_repository = UserRepository()
    return AuthService(user_repository)
