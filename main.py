# AI Traceability: Skills Agent constructed the main FastAPI routing.
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import jwt

from core.cashflow import predict_cashflow
from core.expense_manager import allocate_prepaid_expense
from core.ocr_engine import process_invoice
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

app = FastAPI(title="Mükellef - AI CFO Assistant")


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