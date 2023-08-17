import json
import os
from typing import Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter, Retry

load_dotenv()


MAX_RETRIES = 3
TIMEOUT_SECONDS = 15
BASE_URL = "https://api.nimble.com/api/v1/contacts"


class NimbusClient:
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
        fields: Optional[str] = "first_name,email,description",
        record_type: Optional[str] = "person",
        query: Optional[dict] = None,
    ) -> Optional[dict]:
        """Performs a GET request for contacts in Nimbus

        Args:
            query (Optional[dict]): Query parameters to filter the results. Defaults to None.
            fields (Optional[str]): Fields to return in the response. Defaults to "first_name,email,description".
            record_type (Optional[str]): Record type to filter the results. Defaults to "person".

        Returns:
            Optional[dict]: JSON response as a dictionary, or None if the request failed
        """

        query_params = {"fields": fields, "record_type": record_type, "query": query}

        url = BASE_URL + f"?{self._dict_to_query(query_params)}"

        if query:
            url += f"?query={json.dumps(query)}"

        try:
            response = self.session.get(
                url, headers=self.headers, timeout=TIMEOUT_SECONDS
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            print(f"Request for {url} failed with HTTP error: {e}")
            return None
        except Exception as e:
            print(f"An error occurred for {url}: {str(e)}")
            return None

        return response.json()
