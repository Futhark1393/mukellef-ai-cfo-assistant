# AI Traceability: Skills Agent constructed the main FastAPI routing architecture.
# Temporarily commented out team modules until PRs are merged.
# Developer: Futhark1393

from fastapi import FastAPI
from core.expense_manager import allocate_prepaid_expense

# TODO: Uncomment these after merging teammate PRs
# from core.ocr_engine import process_invoice
# from core.cashflow import predict_cashflow

app = FastAPI(title="Mükellef - AI CFO Assistant")

@app.get("/")
def read_root():
    return {"status": "Mükellef API is running"}

@app.get("/api/expense")
def run_expense_allocation(amount: float, months: int):
    # Trigger the expense allocation module
    return allocate_prepaid_expense(amount, months)

# TODO: Uncomment these after merging teammate PRs
# @app.get("/api/ocr/{invoice_id}")
# def run_ocr(invoice_id: str):
#     return process_invoice(invoice_id)
#
# @app.get("/api/cashflow")
# def run_cashflow(balance: float, rev: float, exp: float):
#     return predict_cashflow(balance, rev, exp)