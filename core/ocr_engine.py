# AI Traceability: Skills Agent designed this mock OCR module to ensure MVP stability during demoday.
# This module provides a mock invoice database and retrieval function for rapid prototyping,
# as well as a theoretical Vision API integration path for production use.

from typing import Optional


# ---------------------------------------------------------------------------
# Mock Invoice Database
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent constructed realistic Turkish B2B invoice
# records covering common expense categories (office supplies, SaaS, logistics)
# to give the demo meaningful, domain-accurate sample data.
MOCK_INVOICE_DB: dict[str, dict] = {
    "INV-2026-001": {
        "invoice_id": "INV-2026-001",
        "vendor_name": "Migros Ticaret A.Ş.",
        "date": "2026-04-15",
        "total_amount": 4720.00,
        "vat_amount": 720.00,
        "currency": "TRY",
        "category": "Office Supplies",
        "description": "Monthly office pantry and cleaning supplies",
        "status": "processed",
    },
    "INV-2026-002": {
        "invoice_id": "INV-2026-002",
        "vendor_name": "Amazon Web Services EMEA SARL",
        "date": "2026-04-22",
        "total_amount": 18_540.00,
        "vat_amount": 2_840.00,
        "currency": "TRY",
        "category": "Cloud & SaaS",
        "description": "AWS monthly infrastructure usage – April 2026",
        "status": "processed",
    },
    "INV-2026-003": {
        "invoice_id": "INV-2026-003",
        "vendor_name": "Aras Kargo",
        "date": "2026-05-01",
        "total_amount": 1_250.00,
        "vat_amount": 190.98,
        "currency": "TRY",
        "category": "Logistics",
        "description": "Domestic parcel shipments – batch #47",
        "status": "pending",
    },
}


# ---------------------------------------------------------------------------
# Core Invoice Retrieval
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented this retrieval function with
# explicit error-handling to return structured JSON-ready responses that
# the FastAPI layer can forward directly to the frontend dashboard.
def process_invoice(invoice_id: str) -> dict:
    """
    Look up and return a single invoice record from the mock database.

    Parameters
    ----------
    invoice_id : str
        Unique identifier for the invoice (e.g. "INV-2026-001").

    Returns
    -------
    dict
        On success: {"success": True, "data": {…invoice fields…}}
        On failure: {"success": False, "error": "..."}
    """
    invoice: Optional[dict] = MOCK_INVOICE_DB.get(invoice_id)

    if invoice is None:
        return {
            "success": False,
            "error": f"Invoice '{invoice_id}' not found in the database.",
        }

    return {
        "success": True,
        "data": invoice,
    }


def list_all_invoices() -> dict:
    """
    Return every invoice in the mock database.

    Returns
    -------
    dict
        {"success": True, "count": int, "data": [list of invoice dicts]}
    """
    invoices = list(MOCK_INVOICE_DB.values())
    return {
        "success": True,
        "count": len(invoices),
        "data": invoices,
    }


# ---------------------------------------------------------------------------
# Theoretical Vision API Integration  (NOT executed – demo / reference only)
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent drafted this theoretical implementation to
# illustrate how a production system would call an LLM Vision API (e.g.
# Google Gemini, OpenAI GPT-4o) to extract structured invoice data from a
# raw image.  The function is intentionally kept as executable-but-guarded
# code so reviewers can see the full intended flow.

def process_invoice_with_vision_api(image_path: str) -> dict:
    """
    **THEORETICAL / NOT ACTIVE**

    Demonstrates how an LLM Vision API could be used to extract structured
    invoice data from a scanned document image.

    Parameters
    ----------
    image_path : str
        Filesystem path to the invoice image (JPEG / PNG / PDF first page).

    Returns
    -------
    dict
        Extracted invoice fields or an error payload.

    Notes
    -----
    To activate this in production you would:
      1. Install the provider SDK  (e.g. ``pip install google-genai``).
      2. Set the API key via environment variable.
      3. Remove the early-return guard below.
    """

    # ── Guard: prevent accidental execution during the demo ──────────
    return {
        "success": False,
        "error": (
            "Vision API integration is theoretical. "
            "Remove this guard and supply an API key to activate."
        ),
    }

    # ── The code below is intentionally unreachable. ─────────────────
    # It serves as a blueprint for the production implementation.

    # import base64
    # import json
    # import os
    # from google import genai          # google-genai SDK
    #
    # # Step 1 – Read and encode the image
    # with open(image_path, "rb") as f:
    #     image_bytes = f.read()
    # encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    #
    # # Step 2 – Build the prompt asking the model for structured output
    # extraction_prompt = (
    #     "You are an expert accountant. Analyse the attached invoice image "
    #     "and return a JSON object with exactly these keys:\n"
    #     "  vendor_name, date (YYYY-MM-DD), total_amount (float), "
    #     "  vat_amount (float), currency, category, description.\n"
    #     "Return ONLY valid JSON, no markdown fences."
    # )
    #
    # # Step 3 – Call the Vision API
    # client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    # response = client.models.generate_content(
    #     model="gemini-2.0-flash",
    #     contents=[
    #         {"text": extraction_prompt},
    #         {
    #             "inline_data": {
    #                 "mime_type": "image/jpeg",
    #                 "data": encoded_image,
    #             }
    #         },
    #     ],
    # )
    #
    # # Step 4 – Parse the structured response
    # extracted_data = json.loads(response.text)
    # extracted_data["status"] = "vision_processed"
    #
    # return {"success": True, "data": extracted_data}


# ---------------------------------------------------------------------------
# Quick local sanity check
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Successful lookup
    result = process_invoice("INV-2026-001")
    print("Single lookup:", result)

    # Missing invoice
    result = process_invoice("INV-9999-000")
    print("Missing invoice:", result)

    # List all
    result = list_all_invoices()
    print(f"All invoices ({result['count']}):", result)

    # Theoretical vision call
    result = process_invoice_with_vision_api("sample_invoice.jpg")
    print("Vision API (theoretical):", result)
