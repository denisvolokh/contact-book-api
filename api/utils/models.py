from sqlalchemy import Column, Index, Integer, String, event
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.sql import func

from .database import Base


class Contact(Base):
    __tablename__ = "Contact"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nimbus_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    description = Column(String)
    search_vector = Column(TSVECTOR)

    __table_args__ = (
        Index("idx_search_vector", search_vector, postgresql_using="gin"),
    )


def update_search_vector(mapper, connection, target):  # type: ignore
    values = [target.first_name, target.last_name, target.email, target.description]
    filtered_values = [item for item in values if item]
    target.search_vector = func.to_tsvector("english", " ".join(filtered_values))


event.listen(Contact, "before_insert", update_search_vector)
event.listen(Contact, "before_update", update_search_vector)
