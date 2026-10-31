2. The FastAPI Endpoint (main.py)
Give him this file. It creates the web API that your HTML dashboard will talk to.
python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from validator import validate_submission

app = FastAPI(title="Resilience Edge API")

# Define the data structure the frontend will send
class ValidationRequest(BaseModel):
    border_name: str
    submitted_documents: List[str]

class HashRequest(BaseModel):
    hs_code: str
    invoice_value: float
    supplier_name: str

@app.get("/api/borders")
def get_borders():
    """Returns a list of available borders for the dropdown menu."""
    return ["beitbridge", "chirundu", "kasumbalesa", "kazungula"]

@app.post("/api/validate")
def run_validation(request: ValidationRequest):
    """
    Takes the border name and the list of documents the user has.
    Returns the gap report.
    """
    result = validate_submission(request.border_name, request.submitted_documents)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.post("/api/hash")
def generate_hash(request: HashRequest):
    """
    Generates a fake SHA-256 hash for the demo.
    (In production, this would use the hashlib library).
    """
    # Generate a mock hash for the demo
    mock_hash = f"SHA256-{hash(request.hs_code + str(request.invoice_value))}"
    
    return {
        "hash": mock_hash,
        "timestamp": "2026-10-26 14:37:00 UTC",
        "verified_against": "ZRA ACI 2026 Guidelines (Source: ZRA.gov.zm)",
        "message": "This hash proves the document data was verified on this date. Any alteration invalidates the hash."
    }
