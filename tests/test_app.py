import uuid

import pytest
from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex}@example.com"


def test_get_activities_returns_at_least_one_activity():
    # Arrange: nothing special to set up for this read-only endpoint

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) >= 1


def test_signup_adds_participant_and_rejects_duplicate():
    # Arrange
    activity_name = "Chess Club"
    email = _unique_email()

    # Act: sign up once
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity_name]["participants"]

    # Act: sign up again
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert duplicate is rejected
    assert response.status_code == 400

    # Cleanup
    client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )


def test_unregister_removes_participant_and_returns_404_on_second_remove():
    # Arrange
    activity_name = "Chess Club"
    email = _unique_email()

    # Act: ensure the participant exists
    signup = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup.status_code == 200

    # Act: remove participant once
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert removal succeeded
    assert response.status_code == 200

    # Act: remove again
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert second removal fails with 404
    assert response.status_code == 404
