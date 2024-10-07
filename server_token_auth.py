from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Secret key for JWT encoding and decoding
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

# In-memory "database" for items and users
db = {}
users_db = {
    "user": {
        "username": os.getenv("APP_USERNAME"),
        "full_name": "Test User",
        "hashed_password": os.getenv('HASHED_PASSWORD'),
        "disabled": False,
    }
}

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


# ███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗███████╗
# ██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝
# █████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║███████╗
# ██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║╚════██║
# ██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║███████║
# ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝

def verify_password(plain_password, hashed_password):
    """
    Verify a plain text password against a hashed password

    Args:
        plain_password (str): The plain text password to verify
        hashed_password (str): The hashed password to verify against

    Returns:
        bool: True if the passwords match, False if they don't
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Get the hashed version of a password

    Args:
        password (str): The plain text password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    """
    Authenticate a user by their username and password

    Args:
        username (str): The username to authenticate
        password (str): The password to authenticate

    Returns:
        dict: The user dictionary if the authentication is successful, False otherwise
    """
    user = users_db.get(username)
    if not user or not verify_password(password, user['hashed_password']):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create an access token for a given payload

    Args:
        data (dict): The payload to encode into the token
        expires_delta (Optional[timedelta], optional): The time delta for the
            expiration of the token. Defaults to None.

    Returns:
        bytes: The encoded access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user based on the given token

    Args:
        token (str): The token to authenticate

    Returns:
        dict: The user dictionary if the authentication is successful, None otherwise

    Raises:
        HTTPException: If the authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = users_db.get(username)
        if user is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return user


# ███████╗███╗   ██╗██████╗ ██████╗  ██████╗ ██╗███╗   ██╗████████╗███████╗
# ██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██║████╗  ██║╚══██╔══╝██╔════╝
# █████╗  ██╔██╗ ██║██║  ██║██████╔╝██║   ██║██║██╔██╗ ██║   ██║   ███████╗
# ██╔══╝  ██║╚██╗██║██║  ██║██╔═══╝ ██║   ██║██║██║╚██╗██║   ██║   ╚════██║
# ███████╗██║ ╚████║██████╔╝██║     ╚██████╔╝██║██║ ╚████║   ██║   ███████║
# ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═╝      ╚═════╝ ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get an access token for a given username and password

    Args:
        form_data (OAuth2PasswordRequestForm): The username and password to authenticate

    Returns:
        dict: The access token and its type

    Raises:
        HTTPException: If the authentication fails
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protect the existing item routes using the new authentication
@app.post("/items/{item_id}",)
async def create_item(item_id: int, item: Item, current_user: dict = Depends(get_current_user)):
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


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int, current_user: dict = Depends(get_current_user)):
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


@app.get("/items/", response_model=List[Item])
async def read_items(current_user: dict = Depends(get_current_user)):
    """
    Read all items

    Returns:
        List[Item]: A list of all items
    """
    return list(db.values())


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, current_user: dict = Depends(get_current_user)):
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


@app.delete("/items/{item_id}")
async def delete_item(item_id: int, current_user: dict = Depends(get_current_user)):
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

