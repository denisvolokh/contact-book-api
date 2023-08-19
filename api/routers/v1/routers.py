from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.utils import schema, search
from api.utils.database import get_db

router = APIRouter()


@router.get("/search", response_model=List[schema.Contact])
def get_search(text: str, db=Depends(get_db)):  # type: ignore
    """Endpoint to synchronously search contacts"""

    results = search.full_text_search(session=db, text=text)

    if not results:
        raise HTTPException(404, detail={"error": "Contact not found"})

    return [dict(row) for row in results]
