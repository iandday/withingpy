from typing import Optional
from pydantic import BaseModel

class WithingsConfig(BaseModel):
    base_url: str
    client_id: str
    client_secret: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

    