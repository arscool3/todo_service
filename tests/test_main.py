import os
from dotenv import load_dotenv

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from todo.database import Base
from todo.main import app, get_db


load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_todo(test_db):
    todo_dict = {'title': 'test', 'description': 'test_description'}
    response = client.post(
        "/todos/",
        json=todo_dict,
    )
    assert response.status_code == 200

    created_todo = response.json()

    assert 'id' in created_todo
    todo_id = created_todo['id']

    response = client.get(f'/todos/{todo_id}')
    assert response.status_code == 200

    data = response.json()

    assert data['title'] == todo_dict['title']
    assert data['description'] == todo_dict['description']


def test_get_not_found_todo(test_db):
    response = client.get('/todos/1')
    assert response.status_code == 404

    data = response.json()

    assert data['detail'] == 'Todo item not found'


def test_update_todo(test_db):

    todo_dict = {'title': 'test', 'description': 'test_description'}
    response = client.post(
        "/todos/",
        json=todo_dict,
    )
    created_todo = response.json()
    todo_id = created_todo['id']

    todo_dict['title'] = 'test2'
    todo_dict['description'] = 'test2 description'

    response = client.put(
        f"/todos/{todo_id}",
        json=todo_dict
    )
    assert response.status_code == 200

    response = client.get(f'/todos/{todo_id}')
    assert response.status_code == 200

    data = response.json()

    assert data['title'] == todo_dict['title']
    assert data['description'] == todo_dict['description']


def test_delete_todo(test_db):
    todo_dict = {'title': 'test', 'description': 'test_description'}
    response = client.post(
        "/todos/",
        json=todo_dict,
    )
    created_todo = response.json()
    todo_id = created_todo['id']

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204

    response = client.get(f'/todos/{todo_id}')
    assert response.status_code == 404

    data = response.json()
    assert data['detail'] == 'Todo item not found'


def test_read_todos(test_db):
    todo_dict = {'title': 'test', 'description': 'test_description'}

    for _ in range(3):

        response = client.post(
            "/todos/",
            json=todo_dict,
        )
        assert response.status_code == 200

    response = client.get(f'/todos/?skip=1&limit=1')
    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1

    todo = data[0]

    assert todo['id'] == 2
    assert todo['title'] == todo_dict['title']
    assert todo['description'] == todo_dict['description']