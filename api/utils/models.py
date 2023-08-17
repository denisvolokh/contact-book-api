from sqlalchemy import Column, Integer, String

from .database import Base


class Contact(Base):
    __tablename__ = "Contact"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nimbus_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    description = Column(String)
