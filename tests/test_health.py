from fastapi.testclient import TestClient

from moira.main import app


def test_healthcheck() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_get_run() -> None:
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/runs",
        json={
            "title": "Neon Alley Opening",
            "location": "six_street",
            "time_label": "evening",
            "weather": "clear",
            "protagonist_name": "Ariel",
            "protagonist_goal": "Find the missing courier",
            "protagonist_traits": ["curious", "restless"],
        },
    )

    assert create_response.status_code == 201
    run = create_response.json()["run"]

    get_response = client.get(f"/api/v1/runs/{run['run_id']}")

    assert get_response.status_code == 200
    assert get_response.json()["run"]["title"] == "Neon Alley Opening"
