import copy
import pytest
from fastapi.testclient import TestClient

# import the FastAPI app and the shared activities structure
from src import app as main_app

client = TestClient(main_app.app)

# preserve a pristine copy of the initial data
_ORIGINAL_ACTIVITIES = copy.deepcopy(main_app.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in‑memory database before each test (AAA: Arrange)."""
    main_app.activities.clear()
    main_app.activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))
    yield
    # no tear‑down needed; fixture is autouse and resets again next time


def test_get_activities():
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    activity = "Chess Club"
    email = "new@student.com"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert resp.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in main_app.activities[activity]["participants"]


def test_signup_duplicate():
    activity = "Chess Club"
    existing = main_app.activities[activity]["participants"][0]

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": existing})

    # Assert
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already signed up"


def test_remove_participant_success():
    activity = "Chess Club"
    participant = main_app.activities[activity]["participants"][0]

    # Act
    resp = client.delete(
        f"/activities/{activity}/participants", params={"email": participant}
    )

    # Assert
    assert resp.status_code == 200
    assert resp.json() == {"message": f"Removed {participant} from {activity}"}
    assert participant not in main_app.activities[activity]["participants"]


def test_remove_participant_not_found():
    activity = "Chess Club"

    # Act
    resp = client.delete(
        f"/activities/{activity}/participants", params={"email": "nobody@mergington.edu"}
    )

    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Participant not found"
