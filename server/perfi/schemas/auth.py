from pydantic import BaseModel
from datetime import datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
