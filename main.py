# AI Traceability: Skills Agent constructed the main FastAPI routing.
# Extended by Skills Agent to add line-item retrieval and invoice listing endpoints.
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.cashflow import predict_cashflow
from core.expense_manager import allocate_prepaid_expense
from core.ocr_engine import (
    get_line_items,
    list_all_invoices,
    process_invoice,
    process_invoice_pages,
)


class CashflowRequest(BaseModel):
    current_balance: float
    monthly_revenue: float
    monthly_expense: float
    months: int = 6


class ExpenseRequest(BaseModel):
    amount: float
    months: int

app = FastAPI(title="Mukellef - AI CFO Assistant")

# Serve the main HTML dashboard
@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/api/expense")
def run_expense_allocation(amount: float, months: int):
    return allocate_prepaid_expense(amount, months)

@app.get("/api/cashflow")
def run_cashflow(balance: float, rev: float, exp: float):
    return predict_cashflow(balance, rev, exp)


@app.post("/api/expense/allocate")
def run_expense_allocation_post(payload: ExpenseRequest):
    return allocate_prepaid_expense(payload.amount, payload.months)


@app.post("/api/cashflow/predict")
def run_cashflow_post(payload: CashflowRequest):
    projections = predict_cashflow(
        payload.current_balance,
        payload.monthly_revenue,
        payload.monthly_expense,
        payload.months,
    )
    return {"success": True, "projections": projections}


# ---------------------------------------------------------------------------
# OCR Endpoints
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent extended the OCR API surface to support
# invoice listing, single invoice detail with line items, line-item-only
# retrieval, per-page breakdown, and file upload with enriched response.

@app.post("/api/ocr/upload")
def upload_invoice(file: UploadFile = File(...)):
    """Upload an invoice file and retrieve its parsed data (mock)."""
    # Use filename as a mock invoice id when possible (e.g. INV-2026-001.pdf)
    invoice_id = (file.filename or "").split(".")[0]
    if not invoice_id:
        invoice_id = "INV-2026-001"
    result = process_invoice(invoice_id)
    if result.get("success"):
        data = result["data"]
        return {
            "success": True,
            "vendor": data.get("vendor_name"),
            "date": data.get("date"),
            "amount": data.get("total_amount"),
            "tax": data.get("total_vat"),
            "description": data.get("description"),
            "page_count": data.get("page_count", 1),
            "line_item_count": len(data.get("line_items", [])),
            "line_items": data.get("line_items", []),
        }
    return {"success": False, "error": result.get("error")}


@app.get("/api/invoices")
def get_all_invoices():
    """Return summary list of all invoices (no line items)."""
    return list_all_invoices()


@app.get("/api/invoice/{invoice_id}")
def get_invoice_detail(invoice_id: str):
    """Return full invoice detail including line items."""
    return process_invoice(invoice_id)


@app.get("/api/invoice/{invoice_id}/line-items")
def get_invoice_line_items(invoice_id: str):
    """Return only the line items for a given invoice."""
    return get_line_items(invoice_id)


@app.get("/api/invoice/{invoice_id}/pages")
def get_invoice_pages(invoice_id: str):
    """Return per-page breakdown of the invoice (mock)."""
    return process_invoice_pages(invoice_id)