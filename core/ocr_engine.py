# AI Traceability: Skills Agent designed this mock OCR module to ensure MVP stability during demoday.
# This module provides a mock invoice database and retrieval function for rapid prototyping,
# as well as a theoretical Vision API integration path for production use.
# Extended by Skills Agent to support multi-page PDF invoices with line-item extraction.

from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from typing import Optional


# ---------------------------------------------------------------------------
# Mock Invoice Database (Enriched with Line Items)
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent constructed realistic Turkish B2B invoice
# records covering common expense categories (office supplies, SaaS, logistics,
# IT equipment) with per-line-item detail to simulate multi-page PDF extraction.
MOCK_INVOICE_DB: dict[str, dict] = {
    "INV-2026-001": {
        "invoice_id": "INV-2026-001",
        "vendor_name": "Migros Ticaret A.S.",
        "date": "2026-04-15",
        "currency": "TRY",
        "category": "Office Supplies",
        "description": "Monthly office pantry and cleaning supplies",
        "status": "processed",
        "page_count": 1,
        "line_items": [
            {
                "line_no": 1,
                "description": "Nescafe Gold 200g",
                "quantity": 10,
                "unit": "pcs",
                "unit_price": 185.00,
                "vat_rate": 10,
                "vat_amount": 185.00,
                "line_total": 2035.00,
            },
            {
                "line_no": 2,
                "description": "A4 Copy Paper 500 sheets",
                "quantity": 20,
                "unit": "pcs",
                "unit_price": 95.00,
                "vat_rate": 10,
                "vat_amount": 190.00,
                "line_total": 2090.00,
            },
            {
                "line_no": 3,
                "description": "Industrial Cleaning Solution 5L",
                "quantity": 2,
                "unit": "pcs",
                "unit_price": 225.00,
                "vat_rate": 20,
                "vat_amount": 90.00,
                "line_total": 540.00,
            },
        ],
        "subtotal": 4000.00,
        "total_vat": 720.00,
        "total_amount": 4720.00,
    },
    "INV-2026-002": {
        "invoice_id": "INV-2026-002",
        "vendor_name": "Amazon Web Services EMEA SARL",
        "date": "2026-04-22",
        "currency": "TRY",
        "category": "Cloud & SaaS",
        "description": "AWS monthly infrastructure usage - April 2026",
        "status": "processed",
        "page_count": 1,
        "line_items": [
            {
                "line_no": 1,
                "description": "EC2 On-Demand (m5.xlarge x 3)",
                "quantity": 720,
                "unit": "hours",
                "unit_price": 12.50,
                "vat_rate": 20,
                "vat_amount": 1800.00,
                "line_total": 10800.00,
            },
            {
                "line_no": 2,
                "description": "S3 Standard Storage",
                "quantity": 500,
                "unit": "GB",
                "unit_price": 1.20,
                "vat_rate": 20,
                "vat_amount": 120.00,
                "line_total": 720.00,
            },
            {
                "line_no": 3,
                "description": "RDS PostgreSQL (db.r5.large)",
                "quantity": 720,
                "unit": "hours",
                "unit_price": 7.50,
                "vat_rate": 20,
                "vat_amount": 1080.00,
                "line_total": 6480.00,
            },
        ],
        "subtotal": 15700.00,
        "total_vat": 2840.00,
        "total_amount": 18540.00,
    },
    "INV-2026-003": {
        "invoice_id": "INV-2026-003",
        "vendor_name": "Aras Kargo",
        "date": "2026-05-01",
        "currency": "TRY",
        "category": "Logistics",
        "description": "Domestic parcel shipments - batch #47",
        "status": "pending",
        "page_count": 1,
        "line_items": [
            {
                "line_no": 1,
                "description": "Standard Parcel (0-5 kg) - Istanbul",
                "quantity": 25,
                "unit": "pcs",
                "unit_price": 32.00,
                "vat_rate": 20,
                "vat_amount": 160.00,
                "line_total": 960.00,
            },
            {
                "line_no": 2,
                "description": "Express Parcel (0-3 kg) - Ankara",
                "quantity": 5,
                "unit": "pcs",
                "unit_price": 42.00,
                "vat_rate": 20,
                "vat_amount": 30.98,
                "line_total": 240.98,
            },
        ],
        "subtotal": 1059.02,
        "total_vat": 190.98,
        "total_amount": 1250.00,
    },
    # AI Traceability: Skills Agent added this multi-page invoice to demonstrate
    # line-item extraction across a 2-page PDF document with 5 line items.
    "INV-2026-004": {
        "invoice_id": "INV-2026-004",
        "vendor_name": "Teknosa Ic ve Dis Tic. A.S.",
        "date": "2026-05-02",
        "currency": "TRY",
        "category": "IT Equipment",
        "description": "Office IT hardware refresh - Q2 2026",
        "status": "processed",
        "page_count": 2,
        "line_items": [
            {
                "line_no": 1,
                "description": "Dell Latitude 5550 Laptop",
                "quantity": 5,
                "unit": "pcs",
                "unit_price": 42000.00,
                "vat_rate": 20,
                "vat_amount": 42000.00,
                "line_total": 252000.00,
            },
            {
                "line_no": 2,
                "description": "Logitech MX Master 3S Mouse",
                "quantity": 10,
                "unit": "pcs",
                "unit_price": 2800.00,
                "vat_rate": 20,
                "vat_amount": 5600.00,
                "line_total": 33600.00,
            },
            {
                "line_no": 3,
                "description": "Samsung 27\" 4K Monitor (S70A)",
                "quantity": 5,
                "unit": "pcs",
                "unit_price": 14500.00,
                "vat_rate": 20,
                "vat_amount": 14500.00,
                "line_total": 87000.00,
            },
            {
                "line_no": 4,
                "description": "USB-C Docking Station",
                "quantity": 5,
                "unit": "pcs",
                "unit_price": 5200.00,
                "vat_rate": 20,
                "vat_amount": 5200.00,
                "line_total": 31200.00,
            },
            {
                "line_no": 5,
                "description": "CAT6 Ethernet Cable 3m",
                "quantity": 20,
                "unit": "pcs",
                "unit_price": 120.00,
                "vat_rate": 20,
                "vat_amount": 480.00,
                "line_total": 2880.00,
            },
        ],
        "subtotal": 338900.00,
        "total_vat": 67780.00,
        "total_amount": 406680.00,
    },
}


# ---------------------------------------------------------------------------
# Normalization Helpers
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added deterministic normalization utilities to
# standardize vendor names, dates, and monetary fields in mock OCR outputs.
def _normalize_vendor_name(vendor_name: str) -> str:
    cleaned = " ".join(str(vendor_name).strip().split())
    if not cleaned:
        return cleaned
    cleaned = re.sub(r"\bA\s*\.?\s*S\s*\.?\b", "A.S.", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bLTD\s*\.?\b", "LTD.", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bSTI\s*\.?\b", "STI.", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bSARL\b", "SARL", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\bGMBH\b", "GMBH", cleaned, flags=re.IGNORECASE)
    return " ".join(cleaned.split())


# AI Traceability: Skills Agent implemented a locale-aware decimal parser to
# normalize amounts like "1.250,50" or "1,250.50" into float values.
def _normalize_decimal(value: object, default: Optional[float] = None) -> Optional[float]:
    if value is None:
        return default
    if isinstance(value, (int, float, Decimal)):
        try:
            return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        except (InvalidOperation, ValueError):
            return default
    text = str(value).strip()
    if not text:
        return default
    text = re.sub(r"[^0-9,.-]", "", text)
    if not text:
        return default
    decimal_sep = None
    if "," in text and "." in text:
        decimal_sep = "," if text.rfind(",") > text.rfind(".") else "."
    elif "," in text:
        decimal_sep = "," if len(text.split(",")[-1]) in (1, 2) else None
    elif "." in text:
        decimal_sep = "." if len(text.split(".")[-1]) in (1, 2) else None
    if decimal_sep == ",":
        normalized = text.replace(".", "").replace(",", ".")
    elif decimal_sep == ".":
        normalized = text.replace(",", "")
    else:
        normalized = text.replace(",", "").replace(".", "")
    try:
        return float(Decimal(normalized).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError):
        return default


# AI Traceability: Skills Agent added ISO-8601 date normalization for common
# Turkish invoice formats (e.g. 15.04.2026, 15/04/2026, 2026-04-15).
def _normalize_date(date_value: str) -> str:
    raw = str(date_value).strip()
    if not raw:
        return raw
    date_formats = (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
    )
    for fmt in date_formats:
        try:
            parsed = datetime.strptime(raw[:10], fmt)
            return parsed.date().isoformat()
        except ValueError:
            continue
    match = re.search(r"(\d{4}[-/.]\d{2}[-/.]\d{2})", raw)
    if match:
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
            try:
                parsed = datetime.strptime(match.group(1), fmt)
                return parsed.date().isoformat()
            except ValueError:
                continue
    match = re.search(r"(\d{2}[-/.]\d{2}[-/.]\d{4})", raw)
    if match:
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y"):
            try:
                parsed = datetime.strptime(match.group(1), fmt)
                return parsed.date().isoformat()
            except ValueError:
                continue
    return raw


# AI Traceability: Skills Agent added deterministic line-item normalization to
# keep quantities, VAT, and totals consistent in mock OCR outputs.
def _normalize_line_item(item: dict, fallback_line_no: int) -> dict:
    normalized = dict(item)
    normalized["line_no"] = int(normalized.get("line_no", fallback_line_no))
    normalized["description"] = " ".join(str(normalized.get("description", "")).split())
    normalized["unit"] = str(normalized.get("unit", "pcs")).strip() or "pcs"

    quantity = _normalize_decimal(normalized.get("quantity"))
    unit_price = _normalize_decimal(normalized.get("unit_price"))
    vat_rate = _normalize_decimal(normalized.get("vat_rate"), default=20.0)
    vat_amount = _normalize_decimal(normalized.get("vat_amount"))
    line_total = _normalize_decimal(normalized.get("line_total"))

    if quantity is not None:
        normalized["quantity"] = quantity
    if unit_price is not None:
        normalized["unit_price"] = unit_price
    if vat_rate is not None:
        normalized["vat_rate"] = vat_rate

    if vat_amount is None and quantity is not None and unit_price is not None and vat_rate is not None:
        vat_amount = _normalize_decimal(quantity * unit_price * (vat_rate / 100))
    if line_total is None and quantity is not None and unit_price is not None:
        base_total = quantity * unit_price
        line_total = _normalize_decimal(base_total + (vat_amount or 0.0))

    if vat_amount is not None:
        normalized["vat_amount"] = vat_amount
    if line_total is not None:
        normalized["line_total"] = line_total

    return normalized


# AI Traceability: Skills Agent centralized invoice normalization to ensure
# consistent header fields and line items for downstream consumers.
def _normalize_invoice_record(invoice: dict) -> dict:
    normalized = dict(invoice)
    normalized["vendor_name"] = _normalize_vendor_name(normalized.get("vendor_name", ""))
    normalized["date"] = _normalize_date(normalized.get("date", ""))
    normalized["total_amount"] = _normalize_decimal(normalized.get("total_amount"))
    normalized["total_vat"] = _normalize_decimal(normalized.get("total_vat"))
    normalized["subtotal"] = _normalize_decimal(normalized.get("subtotal"))

    line_items = normalized.get("line_items", [])
    normalized_items = []
    for idx, item in enumerate(line_items, start=1):
        normalized_items.append(_normalize_line_item(item, idx))
    normalized["line_items"] = normalized_items

    return normalized


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
        On success: {"success": True, "data": {full invoice with line items}}
        On failure: {"success": False, "error": "..."}
    """
    invoice: Optional[dict] = MOCK_INVOICE_DB.get(invoice_id)

    if invoice is None:
        return {
            "success": False,
            "error": f"Invoice '{invoice_id}' not found in the database.",
        }

    # AI Traceability: Skills Agent added normalization to enforce consistent
    # vendor, date, and monetary formats in mock OCR outputs.
    normalized_invoice = _normalize_invoice_record(invoice)

    return {
        "success": True,
        "data": normalized_invoice,
    }


def list_all_invoices() -> dict:
    """
    Return every invoice in the mock database as summary objects (no line items).

    Returns
    -------
    dict
        {"success": True, "count": int, "data": [list of invoice summaries]}
    """
    summaries = []
    for inv in MOCK_INVOICE_DB.values():
        # AI Traceability: Skills Agent normalized summary fields for
        # consistent vendor/date/amount presentation in list views.
        normalized_inv = _normalize_invoice_record(inv)
        summaries.append({
            "invoice_id": normalized_inv["invoice_id"],
            "vendor_name": normalized_inv["vendor_name"],
            "date": normalized_inv["date"],
            "total_amount": normalized_inv["total_amount"],
            "category": normalized_inv["category"],
            "status": normalized_inv["status"],
            "page_count": normalized_inv.get("page_count", 1),
            "line_item_count": len(normalized_inv.get("line_items", [])),
        })
    return {
        "success": True,
        "count": len(summaries),
        "data": summaries,
    }


# ---------------------------------------------------------------------------
# Line-Item Retrieval
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added this function to expose only the
# line-item array for a given invoice, enabling the frontend table component
# to fetch lightweight data without the full invoice envelope.
def get_line_items(invoice_id: str) -> dict:
    """
    Return only the line items array for a given invoice.

    Parameters
    ----------
    invoice_id : str
        Unique identifier for the invoice.

    Returns
    -------
    dict
        On success: {"success": True, "invoice_id": str, "count": int, "data": [line items]}
        On failure: {"success": False, "error": "..."}
    """
    invoice: Optional[dict] = MOCK_INVOICE_DB.get(invoice_id)

    if invoice is None:
        return {
            "success": False,
            "error": f"Invoice '{invoice_id}' not found in the database.",
        }

    # AI Traceability: Skills Agent normalized line items for deterministic
    # VAT and total calculations in mock OCR results.
    normalized_invoice = _normalize_invoice_record(invoice)
    line_items = normalized_invoice.get("line_items", [])
    return {
        "success": True,
        "invoice_id": invoice_id,
        "count": len(line_items),
        "data": line_items,
    }


# ---------------------------------------------------------------------------
# Multi-Page Invoice Processing (Mock)
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent designed this function to simulate per-page
# processing of a multi-page PDF invoice. In production, each page would be
# rendered and sent through the Vision API independently, then merged.
def process_invoice_pages(invoice_id: str) -> dict:
    """
    Return a per-page breakdown of the invoice content.
    In this mock implementation, line items are distributed across pages
    proportionally.

    Parameters
    ----------
    invoice_id : str
        Unique identifier for the invoice.

    Returns
    -------
    dict
        On success: {"success": True, "pages": [{page_no, line_items}, ...]}
        On failure: {"success": False, "error": "..."}
    """
    invoice: Optional[dict] = MOCK_INVOICE_DB.get(invoice_id)

    if invoice is None:
        return {
            "success": False,
            "error": f"Invoice '{invoice_id}' not found in the database.",
        }

    # AI Traceability: Skills Agent normalized per-page payloads for
    # consistent line-item and header formatting.
    normalized_invoice = _normalize_invoice_record(invoice)
    line_items = normalized_invoice.get("line_items", [])
    page_count = normalized_invoice.get("page_count", 1)

    # Distribute line items across pages evenly for the mock
    pages = []
    items_per_page = max(1, len(line_items) // page_count)

    for page_no in range(1, page_count + 1):
        start_idx = (page_no - 1) * items_per_page
        # Last page gets all remaining items
        if page_no == page_count:
            page_items = line_items[start_idx:]
        else:
            page_items = line_items[start_idx : start_idx + items_per_page]

        pages.append({
            "page_no": page_no,
            "line_items": page_items,
            "item_count": len(page_items),
        })

    return {
        "success": True,
        "invoice_id": invoice_id,
        "page_count": page_count,
        "pages": pages,
    }


# ---------------------------------------------------------------------------
# Theoretical: Full Multi-Page PDF OCR Pipeline
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent drafted this theoretical implementation to
# illustrate how a production system would process a multi-page PDF invoice
# through a 5-stage pipeline: PDF Split -> Preprocess -> OCR -> Layout Parse
# -> Line-Item Extraction. The function is guarded to prevent execution.

def extract_line_items_from_pdf(pdf_path: str) -> dict:
    """
    **THEORETICAL / NOT ACTIVE**

    Demonstrates the full 5-stage pipeline for extracting structured line-item
    data from a multi-page PDF invoice using an LLM Vision API.

    Pipeline Stages:
      1. PDF Split    - Convert each PDF page to a high-DPI image
      2. Preprocess   - Deskew, binarize, enhance contrast
      3. OCR / Vision - Send each page image to Gemini Vision API
      4. Layout Parse - Identify header, table, and footer zones
      5. Line Extract - Parse table rows into structured LineItem dicts

    Parameters
    ----------
    pdf_path : str
        Filesystem path to the PDF invoice file.

    Returns
    -------
    dict
        Extracted invoice with line items or an error payload.
    """

    # Guard: prevent accidental execution during the demo
    return {
        "success": False,
        "error": (
            "PDF OCR pipeline is theoretical. "
            "Install PyMuPDF + set GEMINI_API_KEY to activate."
        ),
    }

    # ── The code below is intentionally unreachable. ─────────────────
    # It serves as a blueprint for the production implementation.

    # import base64
    # import json
    # import os
    #
    # import fitz                        # PyMuPDF for PDF rendering
    # from PIL import Image, ImageFilter  # Pillow for image preprocessing
    # from google import genai           # google-genai SDK
    #
    # # ── Stage 1: PDF Split ──────────────────────────────────────────
    # # Render each PDF page as a 300 DPI PNG image
    # doc = fitz.open(pdf_path)
    # page_images = []
    # for page_num in range(len(doc)):
    #     page = doc[page_num]
    #     # 300 DPI = 72 * (300/72) zoom factor
    #     mat = fitz.Matrix(300 / 72, 300 / 72)
    #     pix = page.get_pixmap(matrix=mat)
    #     img_bytes = pix.tobytes("png")
    #     page_images.append(img_bytes)
    # doc.close()
    #
    # # ── Stage 2: Image Preprocessing ────────────────────────────────
    # # Apply contrast enhancement and sharpening for better OCR accuracy
    # processed_images = []
    # for img_bytes in page_images:
    #     from io import BytesIO
    #     img = Image.open(BytesIO(img_bytes))
    #     # Convert to grayscale for consistent OCR
    #     img = img.convert("L")
    #     # Sharpen to improve text edge detection
    #     img = img.filter(ImageFilter.SHARPEN)
    #     # Save back to bytes
    #     buffer = BytesIO()
    #     img.save(buffer, format="PNG")
    #     processed_images.append(buffer.getvalue())
    #
    # # ── Stage 3 & 4: OCR via Vision API + Layout Parsing ───────────
    # # Send all pages to the Vision API with a structured extraction prompt
    # client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    #
    # extraction_prompt = (
    #     "You are an expert accountant processing a multi-page Turkish invoice.\n"
    #     "The attached images are consecutive pages of the SAME invoice.\n"
    #     "Merge any table rows that span across pages.\n\n"
    #     "Return a single JSON object with these keys:\n"
    #     "  vendor_name, date (YYYY-MM-DD), currency, category, description,\n"
    #     "  page_count (int),\n"
    #     "  line_items (array of objects with: line_no, description, quantity,\n"
    #     "              unit, unit_price, vat_rate, vat_amount, line_total),\n"
    #     "  subtotal, total_vat, total_amount.\n\n"
    #     "Return ONLY valid JSON, no markdown fences."
    # )
    #
    # # Build content parts: prompt + all page images
    # content_parts = [{"text": extraction_prompt}]
    # for page_bytes in processed_images:
    #     encoded = base64.b64encode(page_bytes).decode("utf-8")
    #     content_parts.append({
    #         "inline_data": {
    #             "mime_type": "image/png",
    #             "data": encoded,
    #         }
    #     })
    #
    # response = client.models.generate_content(
    #     model="gemini-2.0-flash",
    #     contents=content_parts,
    # )
    #
    # # ── Stage 5: Parse and Validate ─────────────────────────────────
    # extracted_data = json.loads(response.text)
    # extracted_data["status"] = "vision_processed"
    #
    # # Validate line-item totals match the grand total
    # line_sum = sum(item["line_total"] for item in extracted_data.get("line_items", []))
    # grand_total = extracted_data.get("total_amount", 0)
    # if abs(line_sum - grand_total) > grand_total * 0.01:
    #     extracted_data["_validation_warning"] = (
    #         f"Line-item sum ({line_sum}) differs from total ({grand_total}) "
    #         f"by more than 1%."
    #     )
    #
    # return {"success": True, "data": extracted_data}


# ---------------------------------------------------------------------------
# Legacy single-image theoretical function (kept for backward compatibility)
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent preserved this function from the initial MVP
# for backward compatibility. New code should use extract_line_items_from_pdf.
def process_invoice_with_vision_api(image_path: str) -> dict:
    """
    **THEORETICAL / NOT ACTIVE**

    Demonstrates how an LLM Vision API could be used to extract structured
    invoice data from a single scanned document image.

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

    # Guard: prevent accidental execution during the demo
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
    # # Step 1 - Read and encode the image
    # with open(image_path, "rb") as f:
    #     image_bytes = f.read()
    # encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    #
    # # Step 2 - Build the prompt asking the model for structured output
    # extraction_prompt = (
    #     "You are an expert accountant. Analyse the attached invoice image "
    #     "and return a JSON object with exactly these keys:\n"
    #     "  vendor_name, date (YYYY-MM-DD), total_amount (float), "
    #     "  vat_amount (float), currency, category, description.\n"
    #     "Return ONLY valid JSON, no markdown fences."
    # )
    #
    # # Step 3 - Call the Vision API
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
    # # Step 4 - Parse the structured response
    # extracted_data = json.loads(response.text)
    # extracted_data["status"] = "vision_processed"
    #
    # return {"success": True, "data": extracted_data}


# ---------------------------------------------------------------------------
# Quick local sanity check
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("OCR Engine - Sanity Check")
    print("=" * 60)

    # Test 1: Single invoice lookup
    result = process_invoice("INV-2026-001")
    assert result["success"] is True
    assert len(result["data"]["line_items"]) == 3
    print("[PASS] Single invoice lookup with line items")

    # Test 2: Missing invoice
    result = process_invoice("INV-9999-000")
    assert result["success"] is False
    print("[PASS] Missing invoice returns error")

    # Test 3: List all invoices (summaries)
    result = list_all_invoices()
    assert result["success"] is True
    assert result["count"] == 4
    assert "line_items" not in result["data"][0]  # summaries have no line_items
    print(f"[PASS] List all invoices: {result['count']} records")

    # Test 4: Get line items only
    result = get_line_items("INV-2026-002")
    assert result["success"] is True
    assert result["count"] == 3
    print(f"[PASS] Line items for INV-2026-002: {result['count']} items")

    # Test 5: Multi-page invoice
    result = process_invoice("INV-2026-004")
    assert result["success"] is True
    assert result["data"]["page_count"] == 2
    assert len(result["data"]["line_items"]) == 5
    print(f"[PASS] Multi-page invoice INV-2026-004: {result['data']['page_count']} pages, 5 items")

    # Test 6: Per-page breakdown
    result = process_invoice_pages("INV-2026-004")
    assert result["success"] is True
    assert result["page_count"] == 2
    assert len(result["pages"]) == 2
    total_items = sum(p["item_count"] for p in result["pages"])
    assert total_items == 5
    print(f"[PASS] Page breakdown: {result['page_count']} pages, {total_items} total items")

    # Test 7: Theoretical PDF pipeline
    result = extract_line_items_from_pdf("sample_invoice.pdf")
    assert result["success"] is False
    print("[PASS] Theoretical PDF pipeline returns guard message")

    # Test 8: Legacy theoretical vision function
    result = process_invoice_with_vision_api("sample_invoice.jpg")
    assert result["success"] is False
    print("[PASS] Legacy vision API returns guard message")

    print("=" * 60)
    print("ALL CHECKS PASSED")
    print("=" * 60)
