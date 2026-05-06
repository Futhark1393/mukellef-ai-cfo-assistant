from fastapi.testclient import TestClient

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

    print("SUCCESS: MVP integration checks passed")
    return True


if __name__ == "__main__":
    run_tests()
