from fastapi.testclient import TestClient


def test_search_v1(client: TestClient, test_data):
    """Test GET /api/v1/search endpoint

    Args:
        client (TestClient): HTTP client
        test_data: Fixture to load test data
    """

    response = client.get("/api/v1/search?text=john")
    assert response.status_code == 200
    assert response.json()[0]["first_name"] == "John"


def test_search_v2(client: TestClient, test_data):
    """Test GET /api/v2/search endpoint

    Args:
        client (TestClient): HTTP client
        test_data: Fixture to load test data
    """

    response = client.get("/api/v2/search?text=john")

    assert response.status_code == 200

    task_id = response.json().get("task_id")
    assert task_id is not None
