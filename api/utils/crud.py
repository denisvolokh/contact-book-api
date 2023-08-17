from typing import List, Optional

from sqlalchemy.orm import Session

from . import models, schema


def save_contact(db: Session, contact: schema.Contact) -> models.Contact:
    """Performs the save operation for a contact

    Args:
        db (Session): Database session
        contact (schema.Contact): Contact to be saved

    Returns:
        models.Contact: Saved contact
    """

    contact_model = models.Contact(**contact.model_dump())
    db.add(contact_model)
    db.commit()
    db.refresh(contact_model)

    return contact_model


def get_contact(
    db: Session, email: str, nimbus_id: Optional[str] = None
) -> models.Contact:
    """Performs the retrieve operation by email or nimbus id for a contact

    Args:
        db (Session): Database session
        email (str): Email of the contact to be retrieved
        nimbus_id (Optional[str], optional): Nimbus ID of the contact to be retrieved. Defaults to None.

    Returns:
        models.Contact: Retrieved contact
    """

    query = db.query(models.Contact).filter(models.Contact.email == email)

    if nimbus_id:
        return query.filter(models.Contact.nimbus_id == nimbus_id).first()

    return query.first()


def list_contacts(db: Session) -> List[models.Contact]:
    """Perform query to list all contacts

    Args:
        db (Session): Database sesion

    Returns:
        List[models.Contact]: List of contacts
    """

    query = db.query(models.Contact)

    return query.all()
