from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_items_has_items_key():
    r = client.get("/items")
    assert r.status_code == 200
    assert "items" in r.json()


def test_get_existing_item():
    r = client.get("/items/1")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Widget A"
    assert data["price"] == 9.99


def test_get_missing_item_is_404():
    r = client.get("/items/9999")
    assert r.status_code == 404


def test_create_item_return_201():
    payload = {"name": "Test Widget", "price": 5.00}
    r = client.post("/items", json=payload)
    assert r.status_code == 201
    assert r.json()["name"] == "Test Widget"
    assert "id" in r.json()


def test_create_item_missing_price_is_422():
    r = client.post("/items", json={"name": "No Price"})
    assert r.status_code == 422     # Pydantic validation rejects


def test_delete_item_then_404():
    payload = {"name": "Temp", "price": 1.00}
    created = client.post("/items", json=payload)
    item_id = created.json()["id"]
    assert client.delete(f"/items/{item_id}").status_code == 204
    assert client.get(f"/items/{item_id}").status_code == 404


def test_delete_missing_item_is_404():
    assert client.delete("/items/9999").status_code == 404




