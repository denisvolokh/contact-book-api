import concurrent
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry

MAX_RETRIES = 3
TIMEOUT_SECONDS = 15
BASE_URL = "https://api.nimble.com/api/v1/contacts?fields=first_name,email,description&record_type=person"


def fetch_page(session: requests.Session, url: str) -> Optional[dict]:
    """Performs a GET request to the specified URL and returns the response as a JSON object.

    Args:
        session (Session): HTTP session object
        url (str): URL to fetch

    Returns:
        Optional[dict]: JSON response as a dictionary, or None if the request failed
    """

    try:
        response = session.get(url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        print(f"Request for {url} failed with HTTP error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred for {url}: {str(e)}")
        return None


def fetch_all_pages() -> list:
    retry_strategy = Retry(
        total=MAX_RETRIES,
        method_whitelist=["GET"],
        backoff_factor=1,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    with requests.Session() as session:
        session.mount("https://", adapter)

        response = fetch_page(session, BASE_URL)
        if not response:
            print("Failed to fetch initial data")
            return []

        total_pages = response.get("meta").get("pages")

        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_page = {
                executor.submit(fetch_page, session, f"{BASE_URL}&page={page}"): page
                for page in range(1, total_pages + 1)
            }

            results = []
            for future in concurrent.futures.as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    data = future.result()
                    if data:
                        results.extend(data.get("resources"))
                    else:
                        print(f"Failed to fetch page {page}")
                except Exception as e:
                    print(f"An error occurred for page {page}: {str(e)}")

        return results
