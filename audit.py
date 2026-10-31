The Database Schema (SQLite/PostgreSQL)
The backend must save every hash to a table. This is what creates the "audit trail" that SADC/GIZ auditors can query.
sql
CREATE TABLE audit_records (
    id SERIAL PRIMARY KEY,
    check_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    border_name VARCHAR(50) NOT NULL,
    hs_code VARCHAR(20) NOT NULL,
    invoice_value_usd DECIMAL(10, 2) NOT NULL,
    supplier_name VARCHAR(255) NOT NULL,
    document_hash VARCHAR(64) NOT NULL UNIQUE,
    verification_source VARCHAR(255) NOT NULL,
    operator_api_key VARCHAR(64) NOT NULL,
    status VARCHAR(20) DEFAULT 'VERIFIED'
);
________________________________________
2. The Python Logic (audit.py)
This code takes the verified data, combines it into a single string, generates a SHA-256 hash, and saves it to the database.
python
import hashlib
import json
from datetime import datetime, timezone

def generate_audit_record(border_name: str, hs_code: str, invoice_value: float, supplier_name: str, operator_id: str):
    """
    Creates an immutable audit record for a successful document check.
    """
    # 1. Create a timestamp in standard ISO format (crucial for auditors)
    timestamp = datetime.now(timezone.utc).isoformat()

    # 2. Create the payload. This exact string will be hashed.
    # If anyone changes a single character in the future, the hash will break.
    payload = {
        "border": border_name,
        "hs_code": hs_code,
        "invoice_value_usd": invoice_value,
        "supplier": supplier_name,
        "timestamp_utc": timestamp,
        "verified_against": "ZRA ACI 2026 / DGDA Guidelines"
    }
    
    # Convert to JSON string to ensure consistent formatting
    payload_string = json.dumps(payload, sort_keys=True)
    
    # 3. Generate the SHA-256 Hash
    hash_object = hashlib.sha256(payload_string.encode('utf-8'))
    document_hash = hash_object.hexdigest()

    # 4. (In production) Save to database using SQLAlchemy or raw SQL
    # save_to_db(border_name, hs_code, invoice_value, supplier_name, document_hash, timestamp, operator_id)

    # 5. Return the complete Audit Certificate to the frontend
    return {
        "status": "VERIFIED",
        "audit_certificate": {
            "document_hash": f"SHA-256: {document_hash}",
            "timestamp": timestamp,
            "border": border_name,
            "hs_code": hs_code,
            "invoice_value_usd": f"${invoice_value:,.2f}",
            "supplier": supplier_name,
            "verified_against": "ZRA ACI 2026 Guidelines (Source: ZRA.gov.zm)",
            "integrity_message": "This document's integrity is mathematically guaranteed. Any alteration to the data above will invalidate this hash.",
            "operator_id": operator_id
        }
    }



