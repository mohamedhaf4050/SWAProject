import os
import pytest
from fastapi.testclient import TestClient

from .MSModuleApp import app, collection

from dotenv import load_dotenv
load_dotenv()
# client = TestClient(app)
print(os.getenv('KAFKA_BOOTSTRAP_SERVERS'))
print(os.getenv('MONGO_HOST'))
@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def test_client():
    return TestClient(app)


# @pytest.fixture(autouse=True)
# def setup_teardown():
#     # Clear the collection before each test
#     collection.delete_many({})

def test_create_module_with_id_99(client):
    response = client.post(
        "/module/",
        json={
            "module_id": "99",
            "title": "Module 99",
            "description": "Module 99 description",
            "content": {},
            "parent_module_id": None,
            "sub_modules": []
        }
    )
    assert response.status_code == 200
    assert response.status_code == 200
    assert response.json()["title"] == "Module 99"
    assert response.json()["description"] == "Module 99 description"
    assert response.json()["content"] == {}
    assert response.json()["module_id"] == "99"


def test_update_module_99(client):
    response = client.put(
        "/module/99",
        json={
            "module_id": "99",
            "title": "Updated Module 99",
            "description": "Module 99 description",
            "content": {},
            "parent_module_id": None,
            "sub_modules": []
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "module_id": "99",
        "title": "Updated Module 99",
        "description": "Module 99 description",
        "content": {},
        "parent_module_id": None,
        "sub_modules": []
    }


def test_get_module_99(client):
    response = client.get("/module/99")
    assert response.status_code == 200
    assert response.json() == {
        "module_id": "99",
        "title": "Updated Module 99",
        "description": "Module 99 description",
        "content": {},
        "parent_module_id": None,
        "sub_modules": []
    }

def test_delete_module_with_id_99(client):
    response = client.delete("/module/99")
    
    assert response.status_code == 200


def test_get_non_existing_module(client):
    #Arbitary big number
    response = client.get("/module/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Module not found"}

