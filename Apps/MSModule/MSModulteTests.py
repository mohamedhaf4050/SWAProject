import pytest
from fastapi.testclient import TestClient

from .MSModuleApp import app, collection


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    # Clear the collection before each test
    collection.delete_many({})


def test_create_module(test_client):
    # Send a POST request to create a module
    response = test_client.post("/module/", json={
        "module_id": "1",
        "title": "Module 1",
        "description": "This is module 1",
        "content": {},
        "parent_module_id": None,
        "sub_modules": []
    })

    assert response.status_code == 200
    assert response.json()["module_id"] == "1"

    # Check if the module is inserted in the database
    module = collection.find_one({"module_id": "1"})
    assert module is not None
    assert module["title"] == "Module 1"


def test_create_module_with_invalid_parent_module(test_client):
    # Send a POST request to create a module with an invalid parent module
    response = test_client.post("/module/", json={
        "module_id": "2",
        "title": "Module 2",
        "description": "This is module 2",
        "content": {},
        "parent_module_id": "invalid",
        "sub_modules": []
    })

    assert response.status_code == 404
    assert response.json()["detail"] == "Parent module not found"


def test_get_module(test_client):
    # Insert a module in the database
    collection.insert_one({
        "module_id": "3",
        "title": "Module 3",
        "description": "This is module 3",
        "content": {},
        "parent_module_id": None,
        "sub_modules": []
    })

    # Send a GET request to retrieve the module
    response = test_client.get("/module/3")

    assert response.status_code == 200
    assert response.json()["module_id"] == "3"


def test_get_module_not_found(test_client):
    # Send a GET request for a non-existent module
    response = test_client.get("/module/4")

    assert response.status_code == 404
    assert response.json()["detail"] == "Module not found"


def test_get_all_modules(test_client):
    # Insert two modules in the database
    collection.insert_many([
        {
            "module_id": "5",
            "title": "Module 5",
            "description": "This is module 5",
            "content": {},
            "parent_module_id": None,
            "sub_modules": []
        },
        {
            "module_id": "6",
            "title": "Module 6",
            "description": "This is module 6",
            "content": {},
            "parent_module_id": None,
            "sub_modules": []
        }
    ])

    # Send a GET request to retrieve all modules
    response = test_client.get("/module")

    assert response.status_code == 200
    assert len(response.json()) == 2


# def test_update_module(test_client):
#     # Insert a module in the database
#     collection.insert_one({
#         "module_id": "7",
#         "title": "Module 7",
#         "description": "This is module 7",
#         "content": {},
#         "parent_module_id": None,
#         "sub_modules": []
#     })

#     # Send a PUT request to update the module
#     response = test_client.put("/module/7", json={
#         "module_id": "7",
       
