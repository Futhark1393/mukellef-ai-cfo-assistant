# AI Traceability: Skills Agent constructed the main FastAPI routing.
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from core.cashflow import predict_cashflow
from core.expense_manager import allocate_prepaid_expense
from core.ocr_engine import process_invoice


class CashflowRequest(BaseModel):
    current_balance: float
    monthly_revenue: float
    monthly_expense: float
    months: int = 6


class ExpenseRequest(BaseModel):
    amount: float
    months: int

app = FastAPI(title="Mükellef - AI CFO Assistant")

# Ana sayfaya girince HTML dosyasını göster
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


@app.post("/api/ocr/upload")
def upload_invoice(file: UploadFile = File(...)):
    # Use filename as a mock invoice id when possible (e.g. INV-2026-001.pdf).
    invoice_id = (file.filename or "").split(".")[0]
    if not invoice_id:
        invoice_id = "INV-2026-001"
    result = process_invoice(invoice_id)
    if result.get("success"):
        return {
            "vendor": result["data"].get("vendor_name"),
            "date": result["data"].get("date"),
            "amount": result["data"].get("total_amount"),
            "tax": result["data"].get("vat_amount"),
            "description": result["data"].get("description"),
        }
    return {"error": result.get("error")}