from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional


# ---------------------------------------------------------------------------
# Mock Cari Account Database
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added deterministic mock data for cari accounts
# and receipts to enable local testing without external integrations.
MOCK_CARI_ACCOUNTS: dict[str, dict] = {
    "CAR-1001": {
        "account_id": "CAR-1001",
        "customer_name": "Atlas Market",
        "currency": "TRY",
        "balance": 42500.00,
        "status": "active",
        "transactions": [
            {
                "transaction_id": "TRX-1001-001",
                "type": "invoice",
                "date": "2026-04-10",
                "amount": 25000.00,
                "description": "Wholesale invoice INV-2026-021",
            },
            {
                "transaction_id": "TRX-1001-002",
                "type": "invoice",
                "date": "2026-04-24",
                "amount": 17500.00,
                "description": "Wholesale invoice INV-2026-033",
            },
        ],
        "receipts": [],
    },
    "CAR-1002": {
        "account_id": "CAR-1002",
        "customer_name": "Orion Tekstil",
        "currency": "TRY",
        "balance": 12800.00,
        "status": "active",
        "transactions": [
            {
                "transaction_id": "TRX-1002-001",
                "type": "invoice",
                "date": "2026-04-18",
                "amount": 12800.00,
                "description": "Fabric shipment invoice INV-2026-029",
            }
        ],
        "receipts": [],
    },
    "CAR-1003": {
        "account_id": "CAR-1003",
        "customer_name": "Delta Lojistik",
        "currency": "TRY",
        "balance": 6900.00,
        "status": "active",
        "transactions": [
            {
                "transaction_id": "TRX-1003-001",
                "type": "invoice",
                "date": "2026-05-01",
                "amount": 6900.00,
                "description": "Shipment invoice INV-2026-041",
            }
        ],
        "receipts": [],
    },
}


# ---------------------------------------------------------------------------
# Normalization Helpers
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added rounding-safe amount normalization for
# deterministic cari and receipt calculations.
def _normalize_amount(value: object, default: Optional[float] = None) -> Optional[float]:
    if value is None:
        return default
    try:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError):
        return default


# AI Traceability: Skills Agent added deterministic receipt id generation to
# ensure predictable mock receipt outputs.
def _build_receipt_id(account_id: str, payment_date: str, sequence: int) -> str:
    date_token = payment_date.replace("-", "")
    return f"RCPT-{account_id}-{date_token}-{sequence:03d}"


# ---------------------------------------------------------------------------
# Core Cari Operations
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented list logic for cari accounts with
# deterministic mock payloads.
def list_cari_accounts() -> dict:
    summaries = []
    for account in MOCK_CARI_ACCOUNTS.values():
        summaries.append({
            "account_id": account["account_id"],
            "customer_name": account["customer_name"],
            "currency": account["currency"],
            "balance": account["balance"],
            "status": account["status"],
        })
    return {
        "success": True,
        "count": len(summaries),
        "data": summaries,
    }


# AI Traceability: Skills Agent implemented detail retrieval for cari accounts
# to expose transactions and receipts in a single payload.
def get_cari_account(account_id: str) -> dict:
    account = MOCK_CARI_ACCOUNTS.get(account_id)
    if account is None:
        return {
            "success": False,
            "error": f"Cari account '{account_id}' not found.",
        }
    return {
        "success": True,
        "data": account,
    }


# AI Traceability: Skills Agent implemented payment handling to update cari
# balances and generate a receipt payload deterministically.
def record_payment(
    account_id: str,
    amount: float,
    payment_date: str,
    method: str = "bank_transfer",
    reference: Optional[str] = None,
) -> dict:
    account = MOCK_CARI_ACCOUNTS.get(account_id)
    if account is None:
        return {
            "success": False,
            "error": f"Cari account '{account_id}' not found.",
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

    receipt_sequence = len(account.get("receipts", [])) + 1
    receipt_id = _build_receipt_id(account_id, payment_date, receipt_sequence)
    receipt = {
        "receipt_id": receipt_id,
        "account_id": account_id,
        "date": payment_date,
        "amount": normalized_amount,
        "currency": account.get("currency", "TRY"),
        "method": method,
        "reference": reference,
        "status": "collected",
    }

    account["balance"] = _normalize_amount(account["balance"] - normalized_amount, 0.0)
    account.setdefault("receipts", []).append(receipt)
    account.setdefault("transactions", []).append({
        "transaction_id": f"TRX-{account_id}-{receipt_sequence:03d}",
        "type": "payment",
        "date": payment_date,
        "amount": normalized_amount,
        "description": f"Receipt {receipt_id}",
    })

    return {
        "success": True,
        "data": {
            "account": account,
            "receipt": receipt,
        },
    }
