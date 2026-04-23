import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as original_activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    backup = copy.deepcopy(original_activities)
    yield
    original_activities.clear()
    original_activities.update(backup)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (301, 302, 307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_data():
    response = client.get("/activities")
    assert response.status_code == 200
    assert response.json() == original_activities


def test_signup_for_activity_adds_new_participant():
    email = "testuser@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in original_activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "student@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity():
    email = "michael@mergington.edu"
    response = client.delete("/activities/Chess%20Club/participants", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in original_activities["Chess Club"]["participants"]


def test_remove_missing_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants", params={"email": "unknown@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_remove_participant_from_unknown_activity_returns_404():
    response = client.delete("/activities/Unknown%20Club/participants", params={"email": "student@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
