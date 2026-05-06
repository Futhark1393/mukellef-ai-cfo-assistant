from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional


# ---------------------------------------------------------------------------
# Mock Supplier Payment Database
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added deterministic mock data for supplier
# payments (tediyeler) to enable local testing without external integrations.
MOCK_SUPPLIERS: dict[str, dict] = {
    "SUP-2001": {
        "supplier_id": "SUP-2001",
        "supplier_name": "Ege Gida Tedarik",
        "currency": "TRY",
        "balance": 58300.00,
        "status": "active",
        "payments": [],
        "payment_plans": [
            {
                "plan_id": "PLAN-2001-001",
                "due_date": "2026-05-15",
                "amount": 18000.00,
                "status": "scheduled",
                "note": "Weekly grocery supply",
            }
        ],
    },
    "SUP-2002": {
        "supplier_id": "SUP-2002",
        "supplier_name": "Anadolu Ambalaj",
        "currency": "TRY",
        "balance": 22450.00,
        "status": "active",
        "payments": [],
        "payment_plans": [],
    },
    "SUP-2003": {
        "supplier_id": "SUP-2003",
        "supplier_name": "Marmara Kimya",
        "currency": "TRY",
        "balance": 77500.00,
        "status": "active",
        "payments": [],
        "payment_plans": [
            {
                "plan_id": "PLAN-2003-001",
                "due_date": "2026-05-20",
                "amount": 32500.00,
                "status": "scheduled",
                "note": "Raw material shipment",
            }
        ],
    },
}


# ---------------------------------------------------------------------------
# Normalization Helpers
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added rounding-safe amount normalization for
# deterministic supplier payment calculations.
def _normalize_amount(value: object, default: Optional[float] = None) -> Optional[float]:
    if value is None:
        return default
    try:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError):
        return default


# AI Traceability: Skills Agent added deterministic payment id generation to
# keep mock payment identifiers stable across runs.
def _build_payment_id(supplier_id: str, payment_date: str, sequence: int) -> str:
    date_token = payment_date.replace("-", "")
    return f"PAY-{supplier_id}-{date_token}-{sequence:03d}"


# AI Traceability: Skills Agent added deterministic plan id generation to
# keep mock payment plan identifiers stable across runs.
def _build_plan_id(supplier_id: str, due_date: str, sequence: int) -> str:
    date_token = due_date.replace("-", "")
    return f"PLAN-{supplier_id}-{date_token}-{sequence:03d}"


# ---------------------------------------------------------------------------
# Core Supplier Payment Operations
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented list logic for suppliers with
# deterministic mock payloads.
def list_suppliers() -> dict:
    summaries = []
    for supplier in MOCK_SUPPLIERS.values():
        summaries.append({
            "supplier_id": supplier["supplier_id"],
            "supplier_name": supplier["supplier_name"],
            "currency": supplier["currency"],
            "balance": supplier["balance"],
            "status": supplier["status"],
        })
    return {
        "success": True,
        "count": len(summaries),
        "data": summaries,
    }


# AI Traceability: Skills Agent implemented detail retrieval for suppliers
# to expose payments and payment plans in a single payload.
def get_supplier(supplier_id: str) -> dict:
    supplier = MOCK_SUPPLIERS.get(supplier_id)
    if supplier is None:
        return {
            "success": False,
            "error": f"Supplier '{supplier_id}' not found.",
        }
    return {
        "success": True,
        "data": supplier,
    }


# AI Traceability: Skills Agent implemented payment handling to update supplier
# balances and store payment records deterministically.
def record_supplier_payment(
    supplier_id: str,
    amount: float,
    payment_date: str,
    method: str = "bank_transfer",
    reference: Optional[str] = None,
) -> dict:
    supplier = MOCK_SUPPLIERS.get(supplier_id)
    if supplier is None:
        return {
            "success": False,
            "error": f"Supplier '{supplier_id}' not found.",
        }

    normalized_amount = _normalize_amount(amount)
    if normalized_amount is None or normalized_amount <= 0:
        return {
            "success": False,
            "error": "Payment amount must be greater than 0.",
        }

    if not payment_date:
        return {
            "success": False,
            "error": "payment_date is required (YYYY-MM-DD).",
        }

    payment_sequence = len(supplier.get("payments", [])) + 1
    payment_id = _build_payment_id(supplier_id, payment_date, payment_sequence)
    payment = {
        "payment_id": payment_id,
        "supplier_id": supplier_id,
        "date": payment_date,
        "amount": normalized_amount,
        "currency": supplier.get("currency", "TRY"),
        "method": method,
        "reference": reference,
        "status": "paid",
    }

    supplier["balance"] = _normalize_amount(supplier["balance"] - normalized_amount, 0.0)
    supplier.setdefault("payments", []).append(payment)

    return {
        "success": True,
        "data": {
            "supplier": supplier,
            "payment": payment,
        },
    }


# AI Traceability: Skills Agent implemented payment plan scheduling to store
# upcoming supplier payments deterministically.
def schedule_supplier_payment(
    supplier_id: str,
    amount: float,
    due_date: str,
    note: Optional[str] = None,
) -> dict:
    supplier = MOCK_SUPPLIERS.get(supplier_id)
    if supplier is None:
        return {
            "success": False,
            "error": f"Supplier '{supplier_id}' not found.",
        }

    normalized_amount = _normalize_amount(amount)
    if normalized_amount is None or normalized_amount <= 0:
        return {
            "success": False,
            "error": "Scheduled amount must be greater than 0.",
        }

    if not due_date:
        return {
            "success": False,
            "error": "due_date is required (YYYY-MM-DD).",
        }

    plan_sequence = len(supplier.get("payment_plans", [])) + 1
    plan_id = _build_plan_id(supplier_id, due_date, plan_sequence)
    plan = {
        "plan_id": plan_id,
        "supplier_id": supplier_id,
        "due_date": due_date,
        "amount": normalized_amount,
        "currency": supplier.get("currency", "TRY"),
        "status": "scheduled",
        "note": note,
    }

    supplier.setdefault("payment_plans", []).append(plan)

    return {
        "success": True,
        "data": {
            "supplier": supplier,
            "plan": plan,
        },
    }
