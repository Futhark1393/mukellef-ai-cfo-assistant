# AI Traceability: Skills Agent constructed the main FastAPI routing.
# Extended by Skills Agent to add line-item retrieval and invoice listing endpoints.
# Extended by Skills Agent to add all business operations endpoints.
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Optional
import jwt

from core.cashflow import predict_cashflow, predict_cashflow_scenarios
from core.cari import get_cari_account, list_cari_accounts, record_payment
from core.expense_manager import allocate_prepaid_expense
from core.ocr_engine import (
    get_stock_groups,
    get_line_items,
    list_all_invoices,
    process_invoice,
    process_invoice_pages,
)
from core.supplier_payments import (
    get_supplier,
    list_suppliers,
    record_supplier_payment,
    schedule_supplier_payment,
)
from core.burn_rate import analyze_cashflow_health
from core.stock_manager import list_stocks, get_stock, record_movement, valuate_stock
from core.check_manager import list_checks, list_notes, get_check, update_check_status, get_check_summary
from core.bank_tracker import list_bank_accounts, get_bank_account, list_transactions, get_financial_summary
from core.tax_payroll import calculate_kdv, calculate_muhtasar, calculate_payroll, get_tax_summary
from core.employee_tracker import list_employees, get_employee_attendance, get_attendance_summary
from core.vehicle_insurance import list_vehicles, get_vehicle, periodize_insurance
from core.profitability import analyze_profitability
from core import auth, crud, schemas
from core.db import get_db


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------
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


class SupplierPaymentRequest(BaseModel):
    supplier_id: str
    amount: float
    payment_date: str
    method: str = "bank_transfer"
    reference: str | None = None


class SupplierPaymentPlanRequest(BaseModel):
    supplier_id: str
    amount: float
    due_date: str
    note: str | None = None


class BurnRateRequest(BaseModel):
    historical_data: list[dict]
    current_balance: float
    method: str = "average"


class CashflowScenariosRequest(BaseModel):
    current_balance: float
    monthly_revenue: float
    monthly_expense: float
    months: int = 6


class StockMovementRequest(BaseModel):
    stock_id: str
    movement_type: str
    quantity: int
    unit_cost: float = 0.0
    date: str = ""
    description: str = ""


class CheckStatusRequest(BaseModel):
    check_id: str
    new_status: str


app = FastAPI(title="Mukellef - AI CFO Assistant")

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------------------------------------------------------------------------
# Auth Endpoints
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Serve the main HTML dashboard
# ---------------------------------------------------------------------------
@app.get("/")
def read_root():
    return FileResponse("static/index.html")


# ---------------------------------------------------------------------------
# Expense Allocation Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/expense")
def run_expense_allocation(amount: float, months: int):
    return allocate_prepaid_expense(amount, months)


@app.post("/api/expense/allocate")
def run_expense_allocation_post(payload: ExpenseRequest):
    return allocate_prepaid_expense(payload.amount, payload.months)


# ---------------------------------------------------------------------------
# Cashflow Prediction Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/cashflow")
def run_cashflow(balance: float, rev: float, exp: float):
    return predict_cashflow(balance, rev, exp)


@app.post("/api/cashflow/predict")
def run_cashflow_post(payload: CashflowRequest):
    projections = predict_cashflow(
        payload.current_balance,
        payload.monthly_revenue,
        payload.monthly_expense,
        payload.months,
    )
    return {"success": True, "projections": projections}


@app.post("/api/cashflow/scenarios")
def run_cashflow_scenarios(payload: CashflowScenariosRequest):
    result = predict_cashflow_scenarios(
        payload.current_balance,
        payload.monthly_revenue,
        payload.monthly_expense,
        payload.months,
    )
    return {"success": True, "data": result}


# ---------------------------------------------------------------------------
# Burn Rate & Runway Endpoints
# ---------------------------------------------------------------------------
@app.post("/api/burnrate/analyze")
def run_burnrate_analysis(payload: BurnRateRequest):
    result = analyze_cashflow_health(
        payload.historical_data,
        payload.current_balance,
        payload.method,
    )
    return {"success": True, "data": result}


# ---------------------------------------------------------------------------
# Cari Endpoints
# ---------------------------------------------------------------------------
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
@app.post("/api/ocr/upload")
def upload_invoice(file: UploadFile = File(...)):
    """Upload an invoice file and retrieve its parsed data (mock)."""
    invoice_id = (file.filename or "").split(".")[0]
    
    # Check if the uploaded filename matches our mock DB, otherwise fallback
    from core.ocr_engine import MOCK_INVOICE_DB
    if invoice_id not in MOCK_INVOICE_DB:
        invoice_id = "INV-2026-001"
        
    result = process_invoice(invoice_id)
    if result.get("success"):
        data = result["data"]
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
    return list_all_invoices()


@app.get("/api/invoice/{invoice_id}")
def get_invoice_detail(invoice_id: str):
    return process_invoice(invoice_id)


@app.get("/api/invoice/{invoice_id}/line-items")
def get_invoice_line_items(invoice_id: str):
    return get_line_items(invoice_id)


@app.get("/api/invoice/{invoice_id}/pages")
def get_invoice_pages(invoice_id: str):
    return process_invoice_pages(invoice_id)


@app.get("/api/invoice/{invoice_id}/stock-groups")
def get_invoice_stock_groups(invoice_id: str):
    result = get_stock_groups(invoice_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))
    return result


# ---------------------------------------------------------------------------
# Supplier Payment Endpoints (Tediyeler)
# ---------------------------------------------------------------------------
@app.get("/api/suppliers")
def list_supplier_accounts():
    return list_suppliers()


@app.get("/api/suppliers/{supplier_id}")
def get_supplier_account(supplier_id: str):
    result = get_supplier(supplier_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))
    return result


@app.post("/api/suppliers/payments")
def create_supplier_payment(payload: SupplierPaymentRequest):
    result = record_supplier_payment(
        payload.supplier_id,
        payload.amount,
        payload.payment_date,
        payload.method,
        payload.reference,
    )
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))
    return result


@app.post("/api/suppliers/payment-plans")
def create_supplier_payment_plan(payload: SupplierPaymentPlanRequest):
    result = schedule_supplier_payment(
        payload.supplier_id,
        payload.amount,
        payload.due_date,
        payload.note,
    )
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))
    return result


# ---------------------------------------------------------------------------
# Stock & Inventory Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/stock")
def get_all_stocks():
    return list_stocks()


@app.get("/api/stock/{stock_id}")
def get_stock_detail(stock_id: str):
    result = get_stock(stock_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))
    return result


@app.post("/api/stock/movement")
def create_stock_movement(payload: StockMovementRequest):
    result = record_movement(
        payload.stock_id, payload.movement_type, payload.quantity,
        payload.unit_cost, payload.date, payload.description,
    )
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))
    return result


@app.get("/api/stock/{stock_id}/valuation")
def get_stock_valuation(stock_id: str, method: str = "fifo"):
    result = valuate_stock(stock_id, method)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))
    return result


# ---------------------------------------------------------------------------
# Check & Promissory Note Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/checks")
def get_all_checks(check_type: Optional[str] = None, check_status: Optional[str] = None):
    return list_checks(check_type, check_status)


@app.get("/api/checks/summary")
def get_checks_summary():
    return get_check_summary()


@app.get("/api/checks/{check_id}")
def get_check_detail(check_id: str):
    result = get_check(check_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))
    return result


@app.post("/api/checks/status")
def change_check_status(payload: CheckStatusRequest):
    result = update_check_status(payload.check_id, payload.new_status)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))
    return result


@app.get("/api/notes")
def get_all_notes(note_type: Optional[str] = None):
    return list_notes(note_type)


# ---------------------------------------------------------------------------
# Bank & Financial Tracking Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/bank/accounts")
def get_bank_accounts():
    return list_bank_accounts()


@app.get("/api/bank/accounts/{account_id}")
def get_bank_detail(account_id: str):
    result = get_bank_account(account_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))
    return result


@app.get("/api/bank/transactions")
def get_transactions(account_id: Optional[str] = None, txn_type: Optional[str] = None):
    return list_transactions(account_id, txn_type)


@app.get("/api/bank/summary")
def get_bank_summary():
    return get_financial_summary()


# ---------------------------------------------------------------------------
# Tax & Payroll Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/tax/summary")
def get_tax_overview(period: str = "2026-04"):
    return get_tax_summary(period)


@app.get("/api/tax/kdv")
def get_kdv(period: str = "2026-04"):
    return calculate_kdv(period)


@app.get("/api/tax/muhtasar")
def get_muhtasar(period: str = "2026-04"):
    return calculate_muhtasar(period)


@app.get("/api/payroll")
def get_payroll(period: str = "2026-04"):
    return calculate_payroll(period)


# ---------------------------------------------------------------------------
# Employee Attendance Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/employees")
def get_all_employees():
    return list_employees()


@app.get("/api/employees/summary")
def get_employee_summary():
    return get_attendance_summary()


@app.get("/api/employees/{employee_id}")
def get_employee_detail(employee_id: str):
    result = get_employee_attendance(employee_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))
    return result


# ---------------------------------------------------------------------------
# Vehicle & Insurance Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/vehicles")
def get_all_vehicles():
    return list_vehicles()


@app.get("/api/vehicles/{vehicle_id}")
def get_vehicle_detail(vehicle_id: str):
    result = get_vehicle(vehicle_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.get("error"))
    return result


@app.get("/api/vehicles/{vehicle_id}/insurance-periods")
def get_vehicle_insurance_periods(vehicle_id: str):
    result = periodize_insurance(vehicle_id)
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))
    return result


# ---------------------------------------------------------------------------
# Profitability Analysis Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/profitability")
def get_profitability():
    return analyze_profitability()