from typing import List, Optional

from pydantic import BaseModel


class Contact(BaseModel):
    nimbus_id: Optional[str]
    first_name: str
    last_name: str
    email: str
    description: Optional[str]

    class Config:
        from_attributes = True


class TaskStatus(BaseModel):
    task_id: str
    task_status: str


class TaskResult(BaseModel):
    state: str
    status: Optional[str] = None
    result: Optional[List[Contact]] = None
