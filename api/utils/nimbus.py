import json
import logging
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import requests
from pydantic import BaseModel
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT_SECONDS = 15
BASE_URL = "https://api.nimble.com/api/v1/contacts"


class NimbusContact(BaseModel):
    id: str
    fields: Dict[str, Any]


class NimbusContactsResponse(BaseModel):
    resources: List[NimbusContact]
    meta: Optional[Dict[str, Any]]


class NimbusAPIClient:
    """Nimbus API Client"""

    def __init__(self, session: requests.Session) -> None:
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = session
        self.session.mount("https://", adapter)
        self.headers = {
            "Authorization": f"Bearer {os.getenv('NIMBUS_API_KEY')}",
            "Content-Type": "application/json",
        }

    def _dict_to_query(self, query: dict) -> str:
        """Generates a query string from a dictionary ignore any keys with a value of None

        Args:
            query (dict): Query parameters in a dictionary

        Returns:
            str: Query string
        """

        return urlencode({k: v for k, v in query.items() if v is not None})

    def list_contacts(
        self,
        fields: Optional[str] = "first name,last name,email,description",
        record_type: Optional[str] = "person",
        page: Optional[int] = 1,
        query: Optional[dict] = None,
    ) -> Optional[NimbusContactsResponse]:
        """Performs a GET request to list contacts in Nimbus

        Args:
            query (Optional[dict]): Query parameters to filter the results. Defaults to None.
            fields (Optional[str]): Fields to return in the response. Defaults to "first_name,email,description".
            record_type (Optional[str]): Record type to filter the results. Defaults to "person".

        Returns:
            Optional[dict]: JSON response as a dictionary, or None if the request failed
        """

        query_params = {
            "fields": fields,
            "record_type": record_type,
            "query": json.dumps(query) if query else None,
            "page": page,
        }

        (f"Query params: {query_params}")

        url = BASE_URL + f"?{self._dict_to_query(query_params)}"

        try:
            response = self.session.get(
                url, headers=self.headers, timeout=TIMEOUT_SECONDS
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.warning(f"[!] Request for {url} failed with HTTP error: {e}")
            return None
        except Exception as e:
            logger.warning(f"[!] An error occurred for {url}: {str(e)}")
            return None

        return NimbusContactsResponse(**response.json())

    def get_contact(self, id: int) -> Optional[NimbusContactsResponse]:
        """Performs a GET request to get contact in Nimbus

        Args:
            id (int): Contact ID.

        Returns:
            Optional[dict]: JSON response as a dictionary, or None if the request failed
        """

        url = BASE_URL + f"/{id}"

        try:
            response = self.session.get(
                url, headers=self.headers, timeout=TIMEOUT_SECONDS
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.warning(f"[!] Request for {url} failed with HTTP error: {e}")
            return None
        except Exception as e:
            logger.warning(f"[!] An error occurred for {url}: {str(e)}")
            return None

        data = NimbusContactsResponse(**response.json())

        if len(data.resources) == 0:
            return None

        return data
