from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# --- OpenAPI Metadata ---
# This information will be displayed in the Swagger UI documentation.
description = """
A mock API for managing users and their financial transactions. 🚀

You can:
* **Retrieve all users**
* **Retrieve a single user by ID**
* **Retrieve all transactions** (with optional filtering by user)
* **Retrieve all transactions for a specific user**
"""

app = FastAPI(
    title="Mock Transaction API",
    description=description,
    version="1.0.0",
    contact={
        "name": "API Support",
        "url": "http://example.com/contact",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# --- Pydantic Models ---
# These models define the structure of the data for requests and responses.

class Transaction(BaseModel):
    id: int
    user_id: int
    amount: float
    description: str

class User(BaseModel):
    id: int
    name: str
    email: str
    transactions: List[Transaction] = []

# --- Mock Database ---
# In-memory data to simulate a database.

mock_users_db = {
    1: User(id=1, name="Ariel Henryson", email="ariel@example.com"),
    2: User(id=2, name="Jane Doe", email="jane@example.com"),
}

mock_transactions_db = {
    1: Transaction(id=1, user_id=1, amount=100.50, description="Groceries"),
    2: Transaction(id=2, user_id=1, amount=25.00, description="Coffee"),
    3: Transaction(id=3, user_id=2, amount=500.00, description="Rent"),
    4: Transaction(id=4, user_id=1, amount=75.20, description="Dinner"),
}

# --- API Endpoints ---

@app.get("/users", response_model=List[User], tags=["Users"])
def get_users():
    """
    Retrieve a list of all users. The transactions for each user are not populated here.
    """
    return list(mock_users_db.values())

@app.get("/users/{user_id}", response_model=User, tags=["Users"])
def get_user(user_id: int):
    """
    Retrieve a single user by their ID.

    This endpoint will also populate the user's transactions list.
    """
    user = mock_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Populate user's transactions
    user.transactions = [t for t in mock_transactions_db.values() if t.user_id == user_id]
    return user

@app.get("/transactions", response_model=List[Transaction], tags=["Transactions"])
def get_transactions(user_id: Optional[int] = None):
    """
    Retrieve a list of all transactions.

    - You can optionally filter the transactions by providing a `user_id`.
    """
    if user_id is not None:
        # Check if user exists before filtering
        if user_id not in mock_users_db:
             raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
        return [t for t in mock_transactions_db.values() if t.user_id == user_id]
    return list(mock_transactions_db.values())

@app.get("/users/{user_id}/transactions", response_model=List[Transaction], tags=["Users", "Transactions"])
def get_user_transactions(user_id: int):
    """
    Retrieve all transactions for a specific user.

    This provides a direct way to get transactions for a user without fetching the user's full details.
    """
    if user_id not in mock_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return [t for t in mock_transactions_db.values() if t.user_id == user_id]

# To run this application:
# 1. Save the code as a Python file (e.g., `main.py`).
# 2. Make sure you have fastapi and uvicorn installed:
#    pip install fastapi "uvicorn[standard]"
# 3. Run the server from your terminal:
#    uvicorn main:app --reload --port 8001
# 4. Open your browser and go to http://127.0.0.1:8001/docs

if __name__ == "__main__":
    import uvicorn
    # Note: Running with uvicorn.run() is mainly for development.
    # For production, it's better to use the command line as shown above.
    uvicorn.run(app, host="0.0.0.0", port=8001)
