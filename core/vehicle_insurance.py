# AI Traceability: Skills Agent developed the vehicle insurance and expense
# tracking module for the Mukellef AI CFO Assistant.

from copy import deepcopy
from datetime import datetime, date


# ---------------------------------------------------------------------------
# Mock Vehicle & Insurance Data
# ---------------------------------------------------------------------------
MOCK_VEHICLES: dict[str, dict] = {
    "VHC-001": {
        "vehicle_id": "VHC-001",
        "plate": "34 ABC 123",
        "brand": "Ford Transit",
        "year": 2024,
        "type": "Ticari",
        "insurance": {
            "provider": "Axa Sigorta",
            "policy_no": "POL-2026-001",
            "start_date": "2026-01-15",
            "end_date": "2027-01-15",
            "premium": 28000.00,
            "type": "kasko",
        },
        "expenses": [
            {"date": "2026-03-10", "type": "fuel", "amount": 3500.00, "desc": "Yakıt"},
            {"date": "2026-04-05", "type": "maintenance", "amount": 2800.00, "desc": "Periyodik bakım"},
            {"date": "2026-04-20", "type": "fuel", "amount": 3200.00, "desc": "Yakıt"},
        ],
    },
    "VHC-002": {
        "vehicle_id": "VHC-002",
        "plate": "34 DEF 456",
        "brand": "Fiat Doblo",
        "year": 2023,
        "type": "Ticari",
        "insurance": {
            "provider": "Allianz Sigorta",
            "policy_no": "POL-2026-002",
            "start_date": "2026-03-01",
            "end_date": "2027-03-01",
            "premium": 22000.00,
            "type": "kasko",
        },
        "expenses": [
            {"date": "2026-03-15", "type": "fuel", "amount": 2800.00, "desc": "Yakıt"},
            {"date": "2026-04-12", "type": "tire", "amount": 6400.00, "desc": "Lastik değişimi"},
        ],
    },
    "VHC-003": {
        "vehicle_id": "VHC-003",
        "plate": "06 GHI 789",
        "brand": "Toyota Corolla",
        "year": 2025,
        "type": "Binek",
        "insurance": {
            "provider": "Mapfre Sigorta",
            "policy_no": "POL-2026-003",
            "start_date": "2025-11-01",
            "end_date": "2026-11-01",
            "premium": 18500.00,
            "type": "trafik",
        },
        "expenses": [
            {"date": "2026-02-20", "type": "fuel", "amount": 2200.00, "desc": "Yakıt"},
            {"date": "2026-04-01", "type": "fuel", "amount": 2400.00, "desc": "Yakıt"},
        ],
    },
}


# ---------------------------------------------------------------------------
# Core Operations
# ---------------------------------------------------------------------------
def list_vehicles() -> dict:
    summaries = []
    for v in MOCK_VEHICLES.values():
        ins = v.get("insurance", {})
        total_expenses = sum(e["amount"] for e in v.get("expenses", []))
        # Check if insurance is expiring within 30 days
        try:
            end = datetime.strptime(ins.get("end_date", ""), "%Y-%m-%d").date()
            days_left = (end - date.today()).days
        except (ValueError, TypeError):
            days_left = -1

        summaries.append({
            "vehicle_id": v["vehicle_id"],
            "plate": v["plate"],
            "brand": v["brand"],
            "year": v["year"],
            "type": v["type"],
            "insurance_type": ins.get("type", ""),
            "insurance_end": ins.get("end_date", ""),
            "insurance_days_left": days_left,
            "insurance_expiring_soon": 0 < days_left <= 30,
            "total_expenses": round(total_expenses, 2),
        })
    return {"success": True, "count": len(summaries), "data": summaries}


def get_vehicle(vehicle_id: str) -> dict:
    v = MOCK_VEHICLES.get(vehicle_id)
    if v is None:
        return {"success": False, "error": f"Vehicle '{vehicle_id}' not found."}
    return {"success": True, "data": deepcopy(v)}


# AI Traceability: Skills Agent implemented insurance expense periodization
# distributing annual premiums to daily expenses (Donemsellik Ilkesi).
def periodize_insurance(vehicle_id: str) -> dict:
    v = MOCK_VEHICLES.get(vehicle_id)
    if v is None:
        return {"success": False, "error": f"Vehicle '{vehicle_id}' not found."}

    ins = v.get("insurance", {})
    if not ins:
        return {"success": False, "error": "No insurance data."}

    try:
        start = datetime.strptime(ins["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(ins["end_date"], "%Y-%m-%d").date()
    except (ValueError, KeyError):
        return {"success": False, "error": "Invalid insurance dates."}

    total_days = (end - start).days
    if total_days <= 0:
        return {"success": False, "error": "Invalid date range."}

    daily_cost = ins["premium"] / total_days

    # Calculate monthly breakdown
    monthly: dict[str, float] = {}
    current = start
    from calendar import monthrange
    while current < end:
        month_key = current.strftime("%Y-%m")
        _, days_in_month = monthrange(current.year, current.month)
        month_end_day = min(days_in_month, (end - current).days + current.day)
        days_this_month = month_end_day - current.day + 1
        if current.month == end.month and current.year == end.year:
            days_this_month = min(days_this_month, end.day - current.day)
        monthly[month_key] = monthly.get(month_key, 0) + round(daily_cost * days_this_month, 2)
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)

    return {
        "success": True,
        "data": {
            "vehicle_id": vehicle_id,
            "plate": v["plate"],
            "policy_no": ins.get("policy_no"),
            "premium": ins["premium"],
            "period": f"{ins['start_date']} - {ins['end_date']}",
            "total_days": total_days,
            "daily_cost": round(daily_cost, 2),
            "monthly_breakdown": monthly,
        },
    }
