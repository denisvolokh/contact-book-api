from typing import Optional

from pydantic import BaseModel


class Contact(BaseModel):
    nimbus_id: Optional[str]
    first_name: str
    last_name: str
    email: str
    description: Optional[str]

    class Config:
        orm_mode = True
