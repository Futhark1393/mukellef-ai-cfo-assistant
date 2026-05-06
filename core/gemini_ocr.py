import json
import os
import re
from typing import Optional

from google import genai
from google.genai import types

from core.ocr_engine import _normalize_invoice_record


def process_invoice_live(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """
    Takes invoice image bytes, sends it to Gemini Vision API,
    and returns a structured JSON matching the mock database schema.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"success": False, "error": "GEMINI_API_KEY is not set in environment."}

    client = genai.Client(api_key=api_key)

    # We use gemini-2.5-flash as the primary model and add retry logic for rate limits/high demand
    model = "gemini-2.5-flash"

    prompt = """
    You are an expert AI CFO assistant specialized in Turkish invoices.
    Extract the details from the provided invoice image and return ONLY a valid JSON object.
    Do not use markdown blocks like ```json. Return exactly the JSON and nothing else.
    
    The JSON structure MUST perfectly match the following schema:
    {
      "invoice_id": "Extract invoice number (fatura no) or generate a random one like INV-999",
      "vendor_name": "Name of the supplier/vendor",
      "date": "Invoice date in YYYY-MM-DD format",
      "category": "Guess a category based on items: Office Supplies, IT Equipment, Logistics, Cloud & SaaS, General Expense",
      "status": "processed",
      "page_count": 1,
      "line_items": [
        {
          "line_no": 1,
          "description": "Item description",
          "quantity": 1,
          "unit": "pcs",
          "unit_price": 100.0,
          "vat_rate": 20,
          "vat_amount": 20.0,
          "line_total": 120.0
        }
      ],
      "subtotal": 100.0,
      "total_vat": 20.0,
      "total_amount": 120.0
    }
    
    Ensure all numerical values (subtotal, total_vat, total_amount, quantity, unit_price, etc.) are valid floats, and not strings.
    If you cannot find a specific field, do your best to infer or leave it out safely, but never break the JSON structure.
    """

    import time
    max_retries = 3
    response = None
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                )
            )
            break # Success, break the retry loop
        except Exception as e:
            last_error = str(e)
            if "503" in last_error or "429" in last_error or "Quota" in last_error:
                # If rate limited or high demand, wait and try again
                time.sleep(3)
                continue
            else:
                # If it's another error (like 404), fail immediately
                return {"success": False, "error": last_error}

    if not response:
        return {"success": False, "error": f"Failed after {max_retries} attempts. Last error: {last_error}"}

    try:
        # Clean potential markdown wrapping if Gemini ignores instructions
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        text = text.strip()
        
        # Parse JSON
        extracted_data = json.loads(text)
        
        # Normalize to ensure numbers and dates are clean
        normalized_data = _normalize_invoice_record(extracted_data)
        
        return {
            "success": True,
            "data": normalized_data
        }
        
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse OCR response as JSON: {str(e)}\nRaw Response: {text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
