from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# In-memory "database"
db = {}

# Pydantic model for a basic item
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# Create an item
@app.post("/items/{item_id}",)
async def create_item(item_id: int, item: Item):
    """
    Create a new item with the given `item_id` and `item`

    Args:
        item_id (int): The ID of the item to create
        item (Item): The item to create

    Raises:
        HTTPException: If an item with the given `item_id` already exists

    Returns:
        Dict[str, Union[str, Item]]: A dictionary containing the status of the
            request and the created item
    """
    if item_id in db:
        raise HTTPException(status_code=400, detail="Item already exists")
    db[item_id] = item
    return {
        "status": "created",
        "item": item
    }

# Read an item
@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    """
    Read an item by its ID

    Args:
        item_id (int): The ID of the item to read

    Raises:
        HTTPException: If the item does not exist
    """
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]

# Read all items
@app.get("/items/", response_model=List[Item])
async def read_items():
    """
    Read all items

    Returns:
        List[Item]: A list of all items
    """
    return list(db.values())

# Update an item
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    Update an item by its ID

    Args:
        item_id (int): The ID of the item to update
        item (Item): The updated item

    Raises:
        HTTPException: If the item does not exist
    """
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    db[item_id] = item
    return {
        "status": "updated",
        "item": item
    }

# Delete an item
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """
    Delete an item by its ID

    Args:
        item_id (int): The ID of the item to delete

    Raises:
        HTTPException: If the item does not exist

    Returns:
        Dict[str, Union[str, Item]]: A dictionary containing the status of the
            request and the deleted item
    """
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    item = db.pop(item_id)
    return {"status": "deleted",
            "item": item
            }
