PYTHON
"Here is the exact Python logic for the validation engine. It loads the YAML files, checks if the user's submitted documents match the required list, and flags missing documents with their specific consequences (e.g., missing OCC certificate at Kasumbalesa).
The FastAPI code provides three endpoints: one to get the list of borders, one to run the validation, and one to generate the SHA-256 audit hash for the dashboard.

import yaml
import os
from datetime import datetime
from typing import List, Dict, Any

# Define the path to your YAML files
CHECKLIST_DIR = "checklists"

def load_checklist(border_name: str) -> Dict[str, Any]:
    """Loads the YAML file for a specific border."""
    file_path = os.path.join(CHECKLIST_DIR, f"{border_name.lower()}.yaml")
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return None

def validate_submission(border_name: str, submitted_documents: List[str]) -> Dict[str, Any]:
    """
    Compares the submitted documents against the required documents in the YAML file.
    """
    checklist = load_checklist(border_name)
    if not checklist:
        return {"error": f"Checklist for '{border_name}' not found."}

    required_docs = checklist.get("required_documents", [])
    missing_docs = []
    ready_to_submit = True

    # Normalize submitted documents to lowercase for easier matching
    submitted_lower = [doc.lower() for doc in submitted_documents]

    for doc in required_docs:
        doc_name = doc.get("name", "").lower()
        is_required = doc.get("required", False)

        # Check if the required document is missing from the submission
        if is_required and doc_name not in submitted_lower:
            ready_to_submit = False
            missing_docs.append({
                "document": doc.get("name"),
                "issue": "Missing",
                "consequence": doc.get("common_gaps", ["Delay at border"])[0],
                "source": doc.get("source"),
                "confidence": doc.get("confidence")
            })

    # Specific logic for Kasumbalesa (as an example of hardcoded rules)
    if border_name.lower() == "kasumbalesa":
        if "usd cash for border fees" not in submitted_lower:
            missing_docs.append({
                "document": "USD Cash for Border Fees",
                "issue": "Missing",
                "consequence": "Paying in local currency is heavily penalized or rejected",
                "source": "DGDA / OCC",
                "confidence": "medium"
            })
            ready_to_submit = False

    return {
        "border": checklist.get("border"),
        "ready_to_submit": ready_to_submit,
        "documents_required": len(required_docs),
        "documents_submitted": len(submitted_documents),
        "gaps": missing_docs,
        "last_verified": checklist.get("last_updated"),
        "source_summary": checklist.get("source_summary")
    }
