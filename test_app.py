import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Быстрая тестовая база в памяти
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_get_notes_empty(client):
    response = client.get('/notes')
    assert response.status_code == 200
    assert response.json == []

def test_create_note(client):
    response = client.post('/notes', json={"title": "Test", "content": "Hello"})
    assert response.status_code == 201
    assert response.json == {"status": "created"}
