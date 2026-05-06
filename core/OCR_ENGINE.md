# OCR Engine Module

## Purpose
Simulate invoice parsing for the MVP by retrieving structured invoice data from a mock database, enabling demos without external OCR dependencies.

## Logic
- `process_invoice` looks up a single invoice by id and returns a success flag with data or an error.
- `list_all_invoices` returns all mock invoices.
- `process_invoice_with_vision_api` is a guarded blueprint for future Vision API integration.

## Inputs/Outputs
- Inputs
  - `process_invoice(invoice_id: str)`
- Output
  - Success: `{"success": true, "data": {invoice fields}}`
  - Failure: `{"success": false, "error": "..."}`

Example
```
Input: invoice_id="INV-2026-001"
Output: {
  "success": true,
  "data": {
    "invoice_id": "INV-2026-001",
    "vendor_name": "Migros Ticaret A.S.",
    "date": "2026-04-15",
    "total_amount": 4720.0,
    "vat_amount": 720.0,
    "currency": "TRY",
    "category": "Office Supplies",
    "description": "Monthly office pantry and cleaning supplies",
    "status": "processed"
  }
}
```

## AI Traceability
This module was architected with AI assistance to deliver a stable demo path and a clear upgrade path to production OCR.
