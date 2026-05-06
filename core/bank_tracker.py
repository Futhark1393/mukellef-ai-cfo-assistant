# AI Traceability: Skills Agent developed the bank transaction tracking module
# for the Mukellef AI CFO Assistant.

from copy import deepcopy
from typing import Optional


# ---------------------------------------------------------------------------
# Mock Bank Accounts & Transactions
# ---------------------------------------------------------------------------
MOCK_BANK_ACCOUNTS: dict[str, dict] = {
    "BNK-001": {
        "account_id": "BNK-001",
        "bank_name": "Garanti BBVA",
        "account_type": "vadesiz",
        "currency": "TRY",
        "balance": 245680.50,
        "iban": "TR12 0006 2000 0001 2345 6789 00",
    },
    "BNK-002": {
        "account_id": "BNK-002",
        "bank_name": "İş Bankası",
        "account_type": "vadesiz",
        "currency": "TRY",
        "balance": 128350.00,
        "iban": "TR34 0006 4000 0011 2345 6789 00",
    },
    "BNK-003": {
        "account_id": "BNK-003",
        "bank_name": "Ziraat Bankası",
        "account_type": "vadeli",
        "currency": "TRY",
        "balance": 500000.00,
        "iban": "TR56 0001 0000 0012 3456 7890 00",
    },
}

MOCK_TRANSACTIONS: list[dict] = [
    {"id": "TXN-001", "account_id": "BNK-001", "date": "2026-05-01", "type": "income", "amount": 25000.00, "description": "Atlas Market tahsilat", "category": "sales"},
    {"id": "TXN-002", "account_id": "BNK-001", "date": "2026-05-01", "type": "expense", "amount": 18000.00, "description": "Ege Gıda tedarik ödemesi", "category": "supplier"},
    {"id": "TXN-003", "account_id": "BNK-002", "date": "2026-05-02", "type": "income", "amount": 12800.00, "description": "Orion Tekstil tahsilat", "category": "sales"},
    {"id": "TXN-004", "account_id": "BNK-001", "date": "2026-05-02", "type": "expense", "amount": 8450.00, "description": "Ofis malzemeleri", "category": "office"},
    {"id": "TXN-005", "account_id": "BNK-001", "date": "2026-05-03", "type": "expense", "amount": 42000.00, "description": "Dell laptop alımı", "category": "equipment"},
    {"id": "TXN-006", "account_id": "BNK-002", "date": "2026-05-03", "type": "income", "amount": 6900.00, "description": "Delta Lojistik tahsilat", "category": "sales"},
    {"id": "TXN-007", "account_id": "BNK-001", "date": "2026-05-04", "type": "expense", "amount": 15200.00, "description": "Personel maaşları", "category": "payroll"},
    {"id": "TXN-008", "account_id": "BNK-001", "date": "2026-05-04", "type": "expense", "amount": 3500.00, "description": "Kira ödemesi", "category": "rent"},
    {"id": "TXN-009", "account_id": "BNK-002", "date": "2026-05-05", "type": "income", "amount": 38500.00, "description": "Toptan satış geliri", "category": "sales"},
    {"id": "TXN-010", "account_id": "BNK-001", "date": "2026-05-05", "type": "expense", "amount": 2200.00, "description": "Elektrik/Su/Doğalgaz", "category": "utilities"},
    {"id": "TXN-011", "account_id": "BNK-001", "date": "2026-05-06", "type": "expense", "amount": 4800.00, "description": "Sigorta primi", "category": "insurance"},
    {"id": "TXN-012", "account_id": "BNK-002", "date": "2026-05-06", "type": "income", "amount": 15750.00, "description": "Hizmet geliri", "category": "services"},
]


# ---------------------------------------------------------------------------
# Core Operations
# ---------------------------------------------------------------------------
def list_bank_accounts() -> dict:
    accounts = [deepcopy(a) for a in MOCK_BANK_ACCOUNTS.values()]
    total_balance = sum(a["balance"] for a in accounts)
    return {"success": True, "count": len(accounts), "total_balance": round(total_balance, 2), "data": accounts}


def get_bank_account(account_id: str) -> dict:
    account = MOCK_BANK_ACCOUNTS.get(account_id)
    if account is None:
        return {"success": False, "error": f"Bank account '{account_id}' not found."}
    txns = [t for t in MOCK_TRANSACTIONS if t["account_id"] == account_id]
    result = deepcopy(account)
    result["transactions"] = txns
    return {"success": True, "data": result}


def list_transactions(account_id: Optional[str] = None, txn_type: Optional[str] = None) -> dict:
    results = []
    for txn in MOCK_TRANSACTIONS:
        if account_id and txn["account_id"] != account_id:
            continue
        if txn_type and txn["type"] != txn_type:
            continue
        results.append(deepcopy(txn))
    return {"success": True, "count": len(results), "data": results}


def get_financial_summary() -> dict:
    total_income = sum(t["amount"] for t in MOCK_TRANSACTIONS if t["type"] == "income")
    total_expense = sum(t["amount"] for t in MOCK_TRANSACTIONS if t["type"] == "expense")
    net = total_income - total_expense

    income_by_cat: dict[str, float] = {}
    expense_by_cat: dict[str, float] = {}
    for txn in MOCK_TRANSACTIONS:
        cat = txn.get("category", "other")
        if txn["type"] == "income":
            income_by_cat[cat] = income_by_cat.get(cat, 0) + txn["amount"]
        else:
            expense_by_cat[cat] = expense_by_cat.get(cat, 0) + txn["amount"]

    daily: dict[str, dict] = {}
    for txn in MOCK_TRANSACTIONS:
        day = txn["date"]
        if day not in daily:
            daily[day] = {"date": day, "income": 0.0, "expense": 0.0, "net": 0.0}
        if txn["type"] == "income":
            daily[day]["income"] += txn["amount"]
        else:
            daily[day]["expense"] += txn["amount"]
        daily[day]["net"] = round(daily[day]["income"] - daily[day]["expense"], 2)

    total_bank = sum(a["balance"] for a in MOCK_BANK_ACCOUNTS.values())

    return {
        "success": True,
        "data": {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_cashflow": round(net, 2),
            "total_bank_balance": round(total_bank, 2),
            "income_by_category": income_by_cat,
            "expense_by_category": expense_by_cat,
            "daily_breakdown": sorted(daily.values(), key=lambda d: d["date"]),
        },
    }
