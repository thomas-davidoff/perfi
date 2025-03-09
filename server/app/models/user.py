from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import mapped_column, Mapped, relationship
from .base_model import BaseModel
import bcrypt


class User(BaseModel):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    _password_hash: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=False)

    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete"
    )

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, password):
        """
        Hashes a plain password.
        """
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        self._password_hash = hashed_password

    def verify_password(self, password):
        """
        Verifies a password against its hashed version.
        """
        return bcrypt.checkpw(
            password=password.encode("utf-8"),
            hashed_password=self._password_hash,
        )

    def __repr__(self):
        return f"<User {self.username}>"
