import os

from fastapi.testclient import TestClient

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from main import app


def run_tests() -> bool:
    client = TestClient(app)

    # Expense allocation
    expense_payload = {"amount": 12000, "months": 12}
    expense_res = client.post("/api/expense/allocate", json=expense_payload)
    if expense_res.status_code != 200:
        print("Expense endpoint failed", expense_res.status_code)
        return False
    expense_data = expense_res.json()
    if "monthly_amount" not in expense_data:
        print("Expense endpoint missing monthly_amount")
        return False

    # Cashflow prediction
    cashflow_payload = {
        "current_balance": 100000,
        "monthly_revenue": 30000,
        "monthly_expense": 25000,
        "months": 6,
    }
    cashflow_res = client.post("/api/cashflow/predict", json=cashflow_payload)
    if cashflow_res.status_code != 200:
        print("Cashflow endpoint failed", cashflow_res.status_code)
        return False
    cashflow_data = cashflow_res.json()
    projections = cashflow_data.get("projections", [])
    if len(projections) != 6:
        print("Cashflow endpoint returned unexpected projection count")
        return False

    # OCR mock upload
    file_bytes = b"fake-invoice-content"
    ocr_res = client.post(
        "/api/ocr/upload",
        files={"file": ("INV-2026-001.pdf", file_bytes, "application/pdf")},
    )
    if ocr_res.status_code != 200:
        print("OCR endpoint failed", ocr_res.status_code)
        return False
    ocr_data = ocr_res.json()
    if "vendor" not in ocr_data:
        print("OCR endpoint missing vendor")
        return False

    # OCR stock grouping
    grouping_res = client.get("/api/invoice/INV-2026-001/stock-groups")
    if grouping_res.status_code != 200:
        print("Stock grouping endpoint failed", grouping_res.status_code)
        return False
    grouping_data = grouping_res.json()
    if not grouping_data.get("groups"):
        print("Stock grouping endpoint missing groups")
        return False

    # Cari accounts
    cari_res = client.get("/api/cari/accounts")
    if cari_res.status_code != 200:
        print("Cari list endpoint failed", cari_res.status_code)
        return False
    cari_data = cari_res.json()
    if not cari_data.get("data"):
        print("Cari list endpoint missing data")
        return False

    # Cari payment
    cari_payment = {
        "account_id": "CAR-1001",
        "amount": 1000.0,
        "payment_date": "2026-05-05",
        "method": "bank_transfer",
        "reference": "BANK-TRX-001",
    }
    cari_payment_res = client.post("/api/cari/payments", json=cari_payment)
    if cari_payment_res.status_code != 200:
        print("Cari payment endpoint failed", cari_payment_res.status_code)
        return False
    cari_payment_data = cari_payment_res.json()
    if not cari_payment_data.get("data", {}).get("receipt"):
        print("Cari payment endpoint missing receipt")
        return False

    # Supplier list
    supplier_res = client.get("/api/suppliers")
    if supplier_res.status_code != 200:
        print("Supplier list endpoint failed", supplier_res.status_code)
        return False
    supplier_data = supplier_res.json()
    if not supplier_data.get("data"):
        print("Supplier list endpoint missing data")
        return False

    # Supplier payment
    supplier_payment = {
        "supplier_id": "SUP-2001",
        "amount": 2500.0,
        "payment_date": "2026-05-06",
        "method": "eft",
        "reference": "PAY-TRX-009",
    }
    supplier_payment_res = client.post("/api/suppliers/payments", json=supplier_payment)
    if supplier_payment_res.status_code != 200:
        print("Supplier payment endpoint failed", supplier_payment_res.status_code)
        return False
    supplier_payment_data = supplier_payment_res.json()
    if not supplier_payment_data.get("data", {}).get("payment"):
        print("Supplier payment endpoint missing payment")
        return False

    # Supplier payment plan
    supplier_plan = {
        "supplier_id": "SUP-2002",
        "amount": 5400.0,
        "due_date": "2026-05-22",
        "note": "Packaging materials",
    }
    supplier_plan_res = client.post("/api/suppliers/payment-plans", json=supplier_plan)
    if supplier_plan_res.status_code != 200:
        print("Supplier payment plan endpoint failed", supplier_plan_res.status_code)
        return False
    supplier_plan_data = supplier_plan_res.json()
    if not supplier_plan_data.get("data", {}).get("plan"):
        print("Supplier payment plan endpoint missing plan")
        return False

    print("SUCCESS: MVP integration checks passed")
    return True


if __name__ == "__main__":
    run_tests()
