import pytest
from fastapi.testclient import TestClient

# @pytest.fixture
# def client():
#     with TestClient(app) as c:
#         yield c


def test_search_v1(client):
    print(f"========================================== {client.app.routes}")

    response = client.get("/v1/search?text=some_text")
    assert response.status_code == 200


# def test_search_v2(client):
#     response = client.get("/api/v2/search?text=some_text")

#     assert response.status_code == 200

#     # Get the task_id from the response to be used in the next test
#     task_id = response.json().get('task_id')
#     assert task_id is not None
