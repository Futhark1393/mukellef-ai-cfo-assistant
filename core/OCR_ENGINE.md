# OCR Engine Module

## Purpose
Simulate invoice parsing for the MVP by retrieving structured invoice data (including line items) from a mock database, enabling demos without external OCR dependencies.

## Logic
- `process_invoice(invoice_id)` looks up a single invoice by id and returns full detail with line items.
- `list_all_invoices()` returns summary records for all invoices (no line items).
- `get_line_items(invoice_id)` returns only the line-item array for a given invoice.
- `process_invoice_pages(invoice_id)` returns a per-page breakdown of line items (simulates multi-page PDF processing).
- `extract_line_items_from_pdf(pdf_path)` is a guarded theoretical 5-stage pipeline for production PDF OCR.
- `process_invoice_with_vision_api(image_path)` is the legacy single-image Vision API blueprint.

## Data Schema

### Invoice Fields
| Field | Type | Description |
|-------|------|-------------|
| invoice_id | string | Unique identifier (e.g. INV-2026-001) |
| vendor_name | string | Supplier company name |
| date | string | ISO 8601 date |
| currency | string | Currency code (TRY) |
| category | string | Expense category |
| description | string | Invoice description |
| status | string | pending or processed |
| page_count | int | Number of PDF pages |
| line_items | array | List of LineItem objects |
| subtotal | float | Sum before VAT |
| total_vat | float | Total VAT |
| total_amount | float | Grand total |

### LineItem Fields
| Field | Type | Description |
|-------|------|-------------|
| line_no | int | Sequential line number |
| description | string | Product/service name |
| quantity | float | Quantity ordered |
| unit | string | Unit of measure |
| unit_price | float | Price per unit before VAT |
| vat_rate | float | VAT percentage |
| vat_amount | float | VAT for this line |
| line_total | float | Total including VAT |

## API Endpoints
| Method | Route | Description |
|--------|-------|-------------|
| POST | /api/ocr/upload | Upload invoice file, get parsed data |
| GET | /api/invoices | List all invoices (summaries) |
| GET | /api/invoice/{id} | Full invoice with line items |
| GET | /api/invoice/{id}/line-items | Line items only |
| GET | /api/invoice/{id}/pages | Per-page breakdown |

## Production Pipeline (Theoretical)
```
PDF Upload -> Page Split (PyMuPDF) -> Image Preprocess (Pillow) -> Vision API (Gemini) -> Layout Parse -> Line-Item Extract -> Validated JSON
```

## AI Traceability
This module was architected with AI assistance to deliver a stable demo path and a clear upgrade path to production OCR with multi-page PDF support and line-item extraction.
