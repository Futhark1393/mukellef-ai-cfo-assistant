# AI Traceability: Skills Agent constructed the main FastAPI routing.
from fastapi import FastAPI
from fastapi.responses import FileResponse
from core.expense_manager import allocate_prepaid_expense
# from core.ocr_engine import process_invoice
from core.cashflow import predict_cashflow

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