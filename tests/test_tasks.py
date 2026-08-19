import pytest
from app.main import app
from app.models import db


@pytest.fixture
def client():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.get_json()


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Estudar DevOps"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Estudar DevOps"
    assert data["completed"] is False


def test_create_task_without_title(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 400


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Tarefa 1"})
    client.post("/tasks", json={"title": "Tarefa 2"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_complete_task(client):
    created = client.post("/tasks", json={"title": "Tarefa"}).get_json()
    response = client.patch(f"/tasks/{created['id']}/complete")
    assert response.status_code == 200
    assert response.get_json()["completed"] is True


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Tarefa"}).get_json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 200

    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 404
