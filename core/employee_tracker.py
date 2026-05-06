# AI Traceability: Skills Agent developed the employee attendance tracking
# module for the Mukellef AI CFO Assistant.

from copy import deepcopy
from typing import Optional


# ---------------------------------------------------------------------------
# Mock Employee Attendance Data
# ---------------------------------------------------------------------------
MOCK_ATTENDANCE: dict[str, dict] = {
    "EMP-001": {
        "employee_id": "EMP-001",
        "name": "Ahmet Yılmaz",
        "role": "Muhasebe Müdürü",
        "records": [
            {"date": "2026-05-01", "check_in": "08:30", "check_out": "17:45", "hours": 9.25, "status": "present"},
            {"date": "2026-05-02", "check_in": "08:15", "check_out": "18:00", "hours": 9.75, "status": "present"},
            {"date": "2026-05-03", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-04", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-05", "check_in": "08:45", "check_out": "17:30", "hours": 8.75, "status": "present"},
            {"date": "2026-05-06", "check_in": "08:30", "check_out": None, "hours": 0, "status": "active"},
        ],
    },
    "EMP-002": {
        "employee_id": "EMP-002",
        "name": "Fatma Demir",
        "role": "Satış Uzmanı",
        "records": [
            {"date": "2026-05-01", "check_in": "09:00", "check_out": "18:00", "hours": 9.0, "status": "present"},
            {"date": "2026-05-02", "check_in": "08:50", "check_out": "17:50", "hours": 9.0, "status": "present"},
            {"date": "2026-05-03", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-04", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-05", "check_in": None, "check_out": None, "hours": 0, "status": "leave"},
            {"date": "2026-05-06", "check_in": "09:10", "check_out": None, "hours": 0, "status": "active"},
        ],
    },
    "EMP-003": {
        "employee_id": "EMP-003",
        "name": "Mehmet Kaya",
        "role": "Depo Sorumlusu",
        "records": [
            {"date": "2026-05-01", "check_in": "07:00", "check_out": "16:00", "hours": 9.0, "status": "present"},
            {"date": "2026-05-02", "check_in": "07:15", "check_out": "16:30", "hours": 9.25, "status": "present"},
            {"date": "2026-05-03", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-04", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-05", "check_in": "07:00", "check_out": "16:15", "hours": 9.25, "status": "present"},
            {"date": "2026-05-06", "check_in": "07:05", "check_out": None, "hours": 0, "status": "active"},
        ],
    },
    "EMP-004": {
        "employee_id": "EMP-004",
        "name": "Ayşe Çelik",
        "role": "İK Uzmanı",
        "records": [
            {"date": "2026-05-01", "check_in": "09:00", "check_out": "18:00", "hours": 9.0, "status": "present"},
            {"date": "2026-05-02", "check_in": "09:05", "check_out": "18:10", "hours": 9.08, "status": "present"},
            {"date": "2026-05-03", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-04", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-05", "check_in": "08:55", "check_out": "17:50", "hours": 8.92, "status": "present"},
            {"date": "2026-05-06", "check_in": "09:00", "check_out": None, "hours": 0, "status": "active"},
        ],
    },
    "EMP-005": {
        "employee_id": "EMP-005",
        "name": "Can Öztürk",
        "role": "Yazılım Geliştirici",
        "records": [
            {"date": "2026-05-01", "check_in": "10:00", "check_out": "19:30", "hours": 9.5, "status": "present"},
            {"date": "2026-05-02", "check_in": "10:15", "check_out": "20:00", "hours": 9.75, "status": "present"},
            {"date": "2026-05-03", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-04", "check_in": None, "check_out": None, "hours": 0, "status": "weekend"},
            {"date": "2026-05-05", "check_in": "09:45", "check_out": "19:00", "hours": 9.25, "status": "present"},
            {"date": "2026-05-06", "check_in": "10:00", "check_out": None, "hours": 0, "status": "active"},
        ],
    },
}


# ---------------------------------------------------------------------------
# Core Operations
# ---------------------------------------------------------------------------
def list_employees() -> dict:
    summaries = []
    for emp in MOCK_ATTENDANCE.values():
        work_records = [r for r in emp["records"] if r["status"] == "present"]
        total_hours = sum(r["hours"] for r in work_records)
        days_present = len(work_records)
        summaries.append({
            "employee_id": emp["employee_id"],
            "name": emp["name"],
            "role": emp["role"],
            "days_present": days_present,
            "total_hours": round(total_hours, 2),
            "avg_hours": round(total_hours / days_present, 2) if days_present > 0 else 0,
            "today_status": emp["records"][-1]["status"] if emp["records"] else "unknown",
        })
    return {"success": True, "count": len(summaries), "data": summaries}


def get_employee_attendance(employee_id: str) -> dict:
    emp = MOCK_ATTENDANCE.get(employee_id)
    if emp is None:
        return {"success": False, "error": f"Employee '{employee_id}' not found."}
    return {"success": True, "data": deepcopy(emp)}


def get_attendance_summary() -> dict:
    today_active = sum(1 for e in MOCK_ATTENDANCE.values()
                       if e["records"] and e["records"][-1]["status"] == "active")
    today_leave = sum(1 for e in MOCK_ATTENDANCE.values()
                      if e["records"] and e["records"][-1]["status"] == "leave")
    total = len(MOCK_ATTENDANCE)

    all_hours = []
    for emp in MOCK_ATTENDANCE.values():
        for r in emp["records"]:
            if r["status"] == "present":
                all_hours.append(r["hours"])

    return {
        "success": True,
        "data": {
            "total_employees": total,
            "today_active": today_active,
            "today_leave": today_leave,
            "avg_daily_hours": round(sum(all_hours) / len(all_hours), 2) if all_hours else 0,
            "total_hours_this_week": round(sum(all_hours), 2),
        },
    }
