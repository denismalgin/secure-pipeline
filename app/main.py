from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="SecurePipeline API",
    description="Items API - Portfolio project, demo CI/CD with security gates.",
    version="1.0.0",
)


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    in_stock: bool = True


# In-memory store, irl would have PostgreSQL
_items: dict[int, Item] = {
    1: Item(name="Widget A", description="A reliable widget", price=9.99),
    2: Item(name="Widget B", price=24.99, in_stock=False),
}
_next_id = 3


@app.get("/health")
def health_check():
    """Liveness probe, used by Docker HEALTHCHECK and pipeline smoke test."""
    return {"status": "ok", "version": app.version}


@app.get("/items")
def list_items():
    return {"items": {k: v.model_dump() for k, v in _items.items()}}


@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found.")
    return _items[item_id]


@app.post("/items", status_code=201)
def create_item(item: Item):
    global _next_id
    _items[_next_id] = item
    created_id = _next_id
    _next_id += 1
    return {"id": created_id, **item.model_dump()}


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found.")
    del _items[item_id]
