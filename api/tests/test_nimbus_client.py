from unittest.mock import Mock

import pytest
import requests

from api.utils.nimbus import NimbusAPIClient, NimbusContactsResponse


@pytest.fixture
def mock_session():
    return Mock()


@pytest.fixture
def client(mock_session):
    return NimbusAPIClient(session=mock_session)


def test_list_contact_success(client):
    """Test successful request to list contacts in Nimbus

    Args:
        client (NimbusAPIClient): NimbusAPIClient instance
    """

    mock_response_data = {
        "resources": [
            {
                "id": "1",
                "fields": {
                    "first name": "John",
                },
            },
        ],
        "meta": {},
    }

    client.session.get.return_value.json.return_value = mock_response_data
    client.session.get.return_value.raise_for_status = Mock()

    response = client.list_contacts()

    assert isinstance(
        response, NimbusContactsResponse
    ), f"Expected NimbusContactsResponse instance but got {isinstance(response, NimbusContactsResponse)}"
    assert (
        response.resources[0].id == "1"
    ), f"Expected response resource id to be 1 but got {response.resources[0].id}"
    assert (
        response.resources[0].fields["first name"] == "John"
    ), f"Expected response resource first name to be John but got {response.resources[0].fields['first name']}"


def test_get_contact_success(client):
    """Test successful request to get a contact in Nimbus

    Args:
        client (NimbusAPICient): NimbusAPIClient instance
    """

    mock_response_data = {
        "resources": [{"id": "2", "fields": {"name": "John Doe"}}],
        "meta": {},
    }

    client.session.get.return_value.json.return_value = mock_response_data
    client.session.get.return_value.raise_for_status = Mock()

    # Perform the API call
    response = client.get_contact(id=2)

    # Assertions
    assert isinstance(
        response, NimbusContactsResponse
    ), f"Expected NimbusContactsResponse instance but got {isinstance(response, NimbusContactsResponse)}"
    assert (
        response.resources[0].id == "2"
    ), f"Expected response resource id to be 2 but got {response.resources[0].id}"
    assert (
        response.resources[0].fields["name"] == "John Doe"
    ), f"Expected response resource name to be John Doe but got {response.resources[0].fields['name']}"


def test_list_contacts_http_error(client):
    """Test HTTPError raised when listing contacts

    Args:
        client (NimbusAPIClient): NimbusAPIClient instance
    """

    client.session.get.side_effect = requests.HTTPError("Mocked HTTPError")

    response = client.list_contacts()

    assert response is None


def test_get_contact_http_error(client):
    """Test HTTPError raised when getting a contact

    Args:
        client (NimbusAPIClient): NimbusAPIClient instance
    """

    client.session.get.side_effect = requests.HTTPError("Mocked HTTPError")

    response = client.get_contact(id=2)

    assert response is None
