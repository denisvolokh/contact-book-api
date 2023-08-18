from typing import List

from sqlalchemy import func

from . import database, models


def full_text_seach(session: database.SessionLocal, text: str) -> List[models.Contact]:
    """Execute full text search query

    Args:
        text (str): Search text

    Returns:
        List[models.Contact]: List of contacts found
    """

    results = (
        session.query(
            models.Contact.id,
            models.Contact.nimbus_id,
            models.Contact.first_name,
            models.Contact.last_name,
            models.Contact.email,
            models.Contact.description,
        )
        .filter(models.Contact.search_vector.op("@@")(func.plainto_tsquery(text)))
        .all()
    )

    return results
