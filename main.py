# AI Traceability: Skills Agent constructed the main FastAPI routing.
# Extended by Skills Agent to add line-item retrieval and invoice listing endpoints.
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import jwt

from core.cashflow import predict_cashflow
from core.cari import get_cari_account, list_cari_accounts, record_payment
from core.expense_manager import allocate_prepaid_expense
from core.ocr_engine import (
    get_stock_groups,
    get_line_items,
    list_all_invoices,
    process_invoice,
    process_invoice_pages,
)
from core import auth, crud, schemas
from core.db import get_db


class CashflowRequest(BaseModel):
    current_balance: float
    monthly_revenue: float
    monthly_expense: float
    months: int = 6


class ExpenseRequest(BaseModel):
    amount: float
    months: int


class CariPaymentRequest(BaseModel):
    account_id: str
    amount: float
    payment_date: str
    method: str = "bank_transfer"
    reference: str | None = None

app = FastAPI(title="Mukellef - AI CFO Assistant")


@app.post("/api/auth/register", response_model=schemas.TokenResponse)
def register_user(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    try:
        tenant = crud.create_tenant(db, payload.tenant_name, payload.tenant_slug)
        password_hash = auth.hash_password(payload.password)
        user = crud.create_user(db, tenant.id, payload.email, password_hash, payload.role)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tenant or email already exists")

    access_token = auth.create_access_token(user.id, tenant.id, user.role)
    refresh_token = auth.create_refresh_token(user.id, tenant.id, user.role)
    crud.update_refresh_token_hash(db, user, auth.hash_refresh_token(refresh_token))
    return schemas.TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login_user(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    crud.set_last_login(db, user)
    access_token = auth.create_access_token(user.id, user.tenant_id, user.role)
    refresh_token = auth.create_refresh_token(user.id, user.tenant_id, user.role)
    crud.update_refresh_token_hash(db, user, auth.hash_refresh_token(refresh_token))
    return schemas.TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post("/api/auth/refresh", response_model=schemas.TokenResponse)
def refresh_token(payload: schemas.RefreshRequest, db: Session = Depends(get_db)):
    try:
        claims = auth.decode_refresh_token(payload.refresh_token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = crud.get_user_by_id(db, claims.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    expected_hash = auth.hash_refresh_token(payload.refresh_token)
    if not user.refresh_token_hash or user.refresh_token_hash != expected_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = auth.create_access_token(user.id, user.tenant_id, user.role)
    refresh_token_value = auth.create_refresh_token(user.id, user.tenant_id, user.role)
    crud.update_refresh_token_hash(db, user, auth.hash_refresh_token(refresh_token_value))
    return schemas.TokenResponse(access_token=access_token, refresh_token=refresh_token_value)

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
# Cari Endpoints
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added cari account endpoints for mock current
# account tracking and receipt creation.

@app.get("/api/cari/accounts")
def list_cari():
    return list_cari_accounts()


@app.get("/api/cari/accounts/{account_id}")
def get_cari(account_id: str):
    result = get_cari_account(account_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))
    return result


@app.post("/api/cari/payments")
def create_cari_payment(payload: CariPaymentRequest):
    result = record_payment(
        payload.account_id,
        payload.amount,
        payload.payment_date,
        payload.method,
        payload.reference,
    )
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))
    return result


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
        # AI Traceability: Skills Agent added stock grouping payloads to the
        # OCR upload response for accounting-ready summaries.
        stock_groups = get_stock_groups(invoice_id) if data.get("line_items") else None
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
            "stock_groups": stock_groups.get("groups") if stock_groups else [],
            "stock_group_summary": stock_groups.get("summary") if stock_groups else {},
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


@app.get("/api/invoice/{invoice_id}/stock-groups")
# AI Traceability: Skills Agent added a stock grouping endpoint to expose
# line-item group summaries for purchase invoices.
def get_invoice_stock_groups(invoice_id: str):
    """Return stock group summaries for the invoice line items."""
    result = get_stock_groups(invoice_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))
    return result