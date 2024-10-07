from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional
import os
import secrets


load_dotenv()
app = FastAPI()

# In-memory "database"
db = {}

# Basic authentication setup
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verify HTTP Basic credentials against values from the environment variables
    APP_USERNAME and APP_PASSWORD.

    Args:
        credentials (HTTPBasicCredentials): The credentials to verify

    Raises:
        HTTPException: If the credentials are invalid

    Returns:
        HTTPBasicCredentials: The verified credentials
    """
    correct_username = secrets.compare_digest(credentials.username, os.getenv("APP_USERNAME"))
    correct_password = secrets.compare_digest(credentials.password, os.getenv("APP_PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials

# Pydantic model for a basic item
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# Create an item
@app.post("/items/{item_id}")
async def create_item(item_id: int, item: Item, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
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
async def read_item(item_id: int, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Read an item by its ID

    Args:
        item_id (int): The ID of the item to read

    Raises:
        HTTPException: If the item does not exist

    Returns:
        Item: The item read
    """
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Item not found")
    return db[item_id]

# Read all items
@app.get("/items/", response_model=List[Item])
async def read_items(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Read all items

    Returns:
        List[Item]: A list of all items
    """
    return list(db.values())

# Update an item
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    """
    Update an item by its ID

    Args:
        item_id (int): The ID of the item to update
        item (Item): The updated item

    Raises:
        HTTPException: If the item does not exist

    Returns:
        Dict[str, Union[str, Item]]: A dictionary containing the status of the
            request and the updated item
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
async def delete_item(item_id: int, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
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
    return {"status": "deleted", "item": item}
