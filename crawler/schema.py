from pydantic import BaseModel
from datetime import datetime

class RawPage(BaseModel):
    url: str
    title: str
    html: str
    fetched_at: datetime