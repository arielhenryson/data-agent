import random
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# --- OpenAPI Metadata ---
# This information will be displayed in the Swagger UI documentation.
description = """
A mock API for assessing the creditworthiness of bank customers. 🏦

You can submit a customer's name and receive a randomly generated credit profile,
including a score, risk level, and a financing recommendation. 🚀
"""

app = FastAPI(
    title="Creditworthiness Assessment API",
    description=description,
    version="2.0.0",
    contact={
        "name": "API Support",
        "url": "http://example.com/contact",
        "email": "support@example.com",
    },
)

# --- Pydantic Model ---
# This model defines the structure of the data for the response.

class Creditworthiness(BaseModel):
    customer_name: str = Field(..., example="Ariel Henryson", description="The name of the customer being assessed.")
    credit_score: int = Field(..., example=785, description="A score from 300 (very poor) to 850 (excellent).")
    risk_level: str = Field(..., example="Low", description="Categorical risk assessment (Low, Medium, High).")
    recommendation: str = Field(..., example="Approve Loan", description="Recommended action based on the assessment.")
    last_updated: datetime = Field(..., description="UTC timestamp of when the assessment was generated.")


# --- API Endpoint ---

@app.get("/credit-score/", response_model=Creditworthiness, tags=["Credit Scoring"])
def get_credit_score(
    customer_name: str = Query(
        ...,
        min_length=3,
        max_length=50,
        title="Customer Name",
        description="The full name of the customer to assess. Must be between 3 and 50 characters.",
        example="Jane Doe"
    )
):
    """
    Retrieves a randomly generated creditworthiness assessment for a given customer.
    """
    # Generate a random credit score (FICO-like range)
    score = random.randint(300, 850)

    # Determine risk level and recommendation based on the score
    if score >= 740:
        risk_level = "Low"
        recommendation = "Approve Loan"
    elif score >= 670:
        risk_level = "Medium"
        recommendation = "Manual Review Required"
    else:
        risk_level = "High"
        recommendation = "Decline Loan"

    # Create the response object
    assessment = Creditworthiness(
        customer_name=customer_name,
        credit_score=score,
        risk_level=risk_level,
        recommendation=recommendation,
        last_updated=datetime.now(timezone.utc)
    )

    return assessment

# To run this application:
# 1. Save the code as a Python file (e.g., `main.py`).
# 2. Make sure you have fastapi and uvicorn installed:
#    pip install fastapi "uvicorn[standard]"
# 3. Run the server from your terminal:
#    uvicorn main:app --reload --port 8001
# 4. Open your browser and go to http://127.0.0.1:8001/docs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)