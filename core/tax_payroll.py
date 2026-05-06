# AI Traceability: Skills Agent developed the tax and payroll module
# for the Mukellef AI CFO Assistant.

from copy import deepcopy


# ---------------------------------------------------------------------------
# Mock Tax & Payroll Data
# ---------------------------------------------------------------------------
MOCK_EMPLOYEES: list[dict] = [
    {"id": "EMP-001", "name": "Ahmet Yılmaz", "role": "Muhasebe Müdürü", "gross_salary": 45000.00, "start_date": "2024-03-01"},
    {"id": "EMP-002", "name": "Fatma Demir", "role": "Satış Uzmanı", "gross_salary": 32000.00, "start_date": "2024-06-15"},
    {"id": "EMP-003", "name": "Mehmet Kaya", "role": "Depo Sorumlusu", "gross_salary": 28000.00, "start_date": "2025-01-10"},
    {"id": "EMP-004", "name": "Ayşe Çelik", "role": "İK Uzmanı", "gross_salary": 35000.00, "start_date": "2024-09-01"},
    {"id": "EMP-005", "name": "Can Öztürk", "role": "Yazılım Geliştirici", "gross_salary": 55000.00, "start_date": "2025-03-01"},
]

MOCK_INVOICES_FOR_TAX: list[dict] = [
    {"id": "INV-S-001", "type": "sales", "amount": 25000.00, "vat": 5000.00, "date": "2026-04-05"},
    {"id": "INV-S-002", "type": "sales", "amount": 18500.00, "vat": 3700.00, "date": "2026-04-12"},
    {"id": "INV-S-003", "type": "sales", "amount": 42000.00, "vat": 8400.00, "date": "2026-04-20"},
    {"id": "INV-P-001", "type": "purchase", "amount": 15000.00, "vat": 3000.00, "date": "2026-04-03"},
    {"id": "INV-P-002", "type": "purchase", "amount": 8450.00, "vat": 1690.00, "date": "2026-04-15"},
    {"id": "INV-P-003", "type": "purchase", "amount": 22000.00, "vat": 4400.00, "date": "2026-04-22"},
]


# ---------------------------------------------------------------------------
# KDV Calculation
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented KDV (VAT) calculation logic
# comparing sales VAT collected vs purchase VAT paid.
def calculate_kdv(period: str = "2026-04") -> dict:
    sales_vat = sum(i["vat"] for i in MOCK_INVOICES_FOR_TAX if i["type"] == "sales")
    purchase_vat = sum(i["vat"] for i in MOCK_INVOICES_FOR_TAX if i["type"] == "purchase")
    kdv_payable = max(0, sales_vat - purchase_vat)
    kdv_deductible = max(0, purchase_vat - sales_vat)

    return {
        "success": True,
        "data": {
            "period": period,
            "hesaplanan_kdv": round(sales_vat, 2),
            "indirilecek_kdv": round(purchase_vat, 2),
            "odenecek_kdv": round(kdv_payable, 2),
            "devreden_kdv": round(kdv_deductible, 2),
            "sales_invoice_count": sum(1 for i in MOCK_INVOICES_FOR_TAX if i["type"] == "sales"),
            "purchase_invoice_count": sum(1 for i in MOCK_INVOICES_FOR_TAX if i["type"] == "purchase"),
        },
    }


# ---------------------------------------------------------------------------
# Muhtasar Calculation
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented Muhtasar (withholding tax)
# calculation based on employee salaries.
def calculate_muhtasar(period: str = "2026-04") -> dict:
    total_gross = sum(e["gross_salary"] for e in MOCK_EMPLOYEES)
    # Simplified: 15% income tax withholding on gross salaries
    gelir_vergisi = total_gross * 0.15
    # Damga vergisi (stamp tax) ~0.759%
    damga_vergisi = total_gross * 0.00759

    return {
        "success": True,
        "data": {
            "period": period,
            "employee_count": len(MOCK_EMPLOYEES),
            "total_gross_salary": round(total_gross, 2),
            "gelir_vergisi_stopaji": round(gelir_vergisi, 2),
            "damga_vergisi": round(damga_vergisi, 2),
            "total_muhtasar": round(gelir_vergisi + damga_vergisi, 2),
        },
    }


# ---------------------------------------------------------------------------
# Payroll Calculation
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented payroll calculation with
# Turkish social security (SGK) deductions.
def calculate_payroll(period: str = "2026-04") -> dict:
    payslips = []
    for emp in MOCK_EMPLOYEES:
        gross = emp["gross_salary"]
        # SGK İşçi payı: %14
        sgk_worker = gross * 0.14
        # İşsizlik sigortası işçi: %1
        issizlik_worker = gross * 0.01
        # Gelir vergisi matrahı
        gelir_matrahi = gross - sgk_worker - issizlik_worker
        # Gelir vergisi: %15 (simplified first bracket)
        gelir_vergisi = gelir_matrahi * 0.15
        # Damga vergisi
        damga = gross * 0.00759
        # Net maaş
        net = gross - sgk_worker - issizlik_worker - gelir_vergisi - damga
        # SGK İşveren payı: %20.5
        sgk_employer = gross * 0.205
        # İşsizlik sigortası işveren: %2
        issizlik_employer = gross * 0.02
        total_cost = gross + sgk_employer + issizlik_employer

        payslips.append({
            "employee_id": emp["id"],
            "name": emp["name"],
            "role": emp["role"],
            "gross_salary": round(gross, 2),
            "sgk_worker": round(sgk_worker, 2),
            "issizlik_worker": round(issizlik_worker, 2),
            "gelir_vergisi": round(gelir_vergisi, 2),
            "damga_vergisi": round(damga, 2),
            "net_salary": round(net, 2),
            "sgk_employer": round(sgk_employer, 2),
            "issizlik_employer": round(issizlik_employer, 2),
            "total_cost": round(total_cost, 2),
        })

    total_net = sum(p["net_salary"] for p in payslips)
    total_cost = sum(p["total_cost"] for p in payslips)

    return {
        "success": True,
        "data": {
            "period": period,
            "employee_count": len(payslips),
            "total_net_salary": round(total_net, 2),
            "total_employer_cost": round(total_cost, 2),
            "payslips": payslips,
        },
    }


def get_tax_summary(period: str = "2026-04") -> dict:
    kdv = calculate_kdv(period)
    muhtasar = calculate_muhtasar(period)
    payroll = calculate_payroll(period)
    return {
        "success": True,
        "data": {
            "period": period,
            "kdv": kdv["data"],
            "muhtasar": muhtasar["data"],
            "payroll_summary": {
                "employee_count": payroll["data"]["employee_count"],
                "total_net": payroll["data"]["total_net_salary"],
                "total_cost": payroll["data"]["total_employer_cost"],
            },
        },
    }
