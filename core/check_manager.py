# AI Traceability: Skills Agent developed the check and promissory note management
# module for the Mukellef AI CFO Assistant.

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from copy import deepcopy


# ---------------------------------------------------------------------------
# Mock Check/Senet Database
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added deterministic mock data for checks and
# promissory notes to enable local testing.
MOCK_CHECKS_DB: dict[str, dict] = {
    "CHK-R-001": {
        "check_id": "CHK-R-001",
        "type": "received",  # alınan
        "drawer": "Atlas Market",
        "amount": 25000.00,
        "currency": "TRY",
        "issue_date": "2026-04-10",
        "due_date": "2026-06-10",
        "bank": "Garanti BBVA",
        "status": "portfolio",  # portföyde
        "description": "Mal bedeli ödemesi",
    },
    "CHK-R-002": {
        "check_id": "CHK-R-002",
        "type": "received",
        "drawer": "Orion Tekstil",
        "amount": 12800.00,
        "currency": "TRY",
        "issue_date": "2026-04-18",
        "due_date": "2026-05-18",
        "bank": "İş Bankası",
        "status": "clearing",  # takasta
        "description": "Kumaş sipariş ödemesi",
    },
    "CHK-R-003": {
        "check_id": "CHK-R-003",
        "type": "received",
        "drawer": "Delta Lojistik",
        "amount": 6900.00,
        "currency": "TRY",
        "issue_date": "2026-05-01",
        "due_date": "2026-07-01",
        "bank": "Yapı Kredi",
        "status": "portfolio",
        "description": "Nakliye ödemesi",
    },
    "CHK-G-001": {
        "check_id": "CHK-G-001",
        "type": "given",  # verilen
        "payee": "Ege Gıda Tedarik",
        "amount": 18000.00,
        "currency": "TRY",
        "issue_date": "2026-04-20",
        "due_date": "2026-05-20",
        "bank": "Garanti BBVA",
        "status": "pending",  # beklemede
        "description": "Haftalık tedarik ödemesi",
    },
    "CHK-G-002": {
        "check_id": "CHK-G-002",
        "type": "given",
        "payee": "Marmara Kimya",
        "amount": 32500.00,
        "currency": "TRY",
        "issue_date": "2026-05-01",
        "due_date": "2026-06-15",
        "bank": "Ziraat Bankası",
        "status": "pending",
        "description": "Hammadde ödemesi",
    },
    "CHK-G-003": {
        "check_id": "CHK-G-003",
        "type": "given",
        "payee": "Anadolu Ambalaj",
        "amount": 15000.00,
        "currency": "TRY",
        "issue_date": "2026-03-15",
        "due_date": "2026-04-15",
        "bank": "Halkbank",
        "status": "paid",  # ödendi
        "description": "Ambalaj malzemesi",
    },
}

# Senet (Promissory Notes)
MOCK_NOTES_DB: dict[str, dict] = {
    "SNT-R-001": {
        "note_id": "SNT-R-001",
        "type": "received",
        "drawer": "Atlas Market",
        "amount": 17500.00,
        "currency": "TRY",
        "issue_date": "2026-04-24",
        "due_date": "2026-07-24",
        "status": "portfolio",
        "description": "Toptan satış senedi",
    },
    "SNT-G-001": {
        "note_id": "SNT-G-001",
        "type": "given",
        "payee": "Ege Gıda Tedarik",
        "amount": 40300.00,
        "currency": "TRY",
        "issue_date": "2026-04-25",
        "due_date": "2026-08-25",
        "status": "pending",
        "description": "Hammadde tedarik senedi",
    },
}


# ---------------------------------------------------------------------------
# Core Operations
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented check and note listing/filtering.
def list_checks(check_type: Optional[str] = None, status: Optional[str] = None) -> dict:
    results = []
    for check in MOCK_CHECKS_DB.values():
        if check_type and check["type"] != check_type:
            continue
        if status and check["status"] != status:
            continue
        results.append(deepcopy(check))
    return {"success": True, "count": len(results), "data": results}


def list_notes(note_type: Optional[str] = None) -> dict:
    results = []
    for note in MOCK_NOTES_DB.values():
        if note_type and note["type"] != note_type:
            continue
        results.append(deepcopy(note))
    return {"success": True, "count": len(results), "data": results}


def get_check(check_id: str) -> dict:
    check = MOCK_CHECKS_DB.get(check_id)
    if check is None:
        return {"success": False, "error": f"Check '{check_id}' not found."}
    return {"success": True, "data": deepcopy(check)}


# AI Traceability: Skills Agent implemented check status updates for clearing
# and payment tracking.
def update_check_status(check_id: str, new_status: str) -> dict:
    valid_statuses = ("portfolio", "clearing", "paid", "bounced", "endorsed", "pending")
    check = MOCK_CHECKS_DB.get(check_id)
    if check is None:
        return {"success": False, "error": f"Check '{check_id}' not found."}
    if new_status not in valid_statuses:
        return {"success": False, "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
    check["status"] = new_status
    return {"success": True, "data": deepcopy(check)}


# AI Traceability: Skills Agent implemented summary calculations for dashboard
# display of receivable/payable totals.
def get_check_summary() -> dict:
    received = [c for c in MOCK_CHECKS_DB.values() if c["type"] == "received"]
    given = [c for c in MOCK_CHECKS_DB.values() if c["type"] == "given"]

    total_receivable = sum(c["amount"] for c in received if c["status"] in ("portfolio", "clearing"))
    total_payable = sum(c["amount"] for c in given if c["status"] == "pending")
    clearing_count = sum(1 for c in received if c["status"] == "clearing")
    clearing_amount = sum(c["amount"] for c in received if c["status"] == "clearing")

    notes_received = [n for n in MOCK_NOTES_DB.values() if n["type"] == "received"]
    notes_given = [n for n in MOCK_NOTES_DB.values() if n["type"] == "given"]
    notes_receivable = sum(n["amount"] for n in notes_received if n["status"] in ("portfolio",))
    notes_payable = sum(n["amount"] for n in notes_given if n["status"] == "pending")

    return {
        "success": True,
        "data": {
            "checks": {
                "total_receivable": total_receivable,
                "total_payable": total_payable,
                "received_count": len(received),
                "given_count": len(given),
                "clearing_count": clearing_count,
                "clearing_amount": clearing_amount,
            },
            "notes": {
                "total_receivable": notes_receivable,
                "total_payable": notes_payable,
                "received_count": len(notes_received),
                "given_count": len(notes_given),
            },
            "grand_total_receivable": total_receivable + notes_receivable,
            "grand_total_payable": total_payable + notes_payable,
        },
    }
