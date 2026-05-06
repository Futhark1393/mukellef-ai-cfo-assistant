# AI Traceability: Skills Agent developed the stock and inventory management module
# with FIFO/LIFO valuation methods for the Mukellef AI CFO Assistant.

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from copy import deepcopy


# ---------------------------------------------------------------------------
# Mock Stock Database
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added deterministic mock data for stock/inventory
# to enable local testing of in/out tracking and valuation methods.
MOCK_STOCK_DB: dict[str, dict] = {
    "STK-001": {
        "stock_id": "STK-001",
        "name": "Nescafe Gold 200g",
        "category": "consumables",
        "unit": "adet",
        "current_quantity": 150,
        "min_quantity": 20,
        "location": "Depo A",
        "movements": [
            {"id": "MOV-001", "type": "in", "date": "2026-04-01", "quantity": 100, "unit_cost": 185.00, "description": "Migros alış faturası INV-2026-001"},
            {"id": "MOV-002", "type": "in", "date": "2026-04-15", "quantity": 80, "unit_cost": 190.00, "description": "Migros alış faturası INV-2026-012"},
            {"id": "MOV-003", "type": "out", "date": "2026-04-20", "quantity": 30, "unit_cost": 0, "description": "Satış - Atlas Market"},
        ],
    },
    "STK-002": {
        "stock_id": "STK-002",
        "name": "A4 Kağıt 500 yaprak",
        "category": "consumables",
        "unit": "paket",
        "current_quantity": 45,
        "min_quantity": 10,
        "location": "Depo A",
        "movements": [
            {"id": "MOV-004", "type": "in", "date": "2026-04-01", "quantity": 50, "unit_cost": 95.00, "description": "Migros alış faturası INV-2026-001"},
            {"id": "MOV-005", "type": "out", "date": "2026-04-18", "quantity": 5, "unit_cost": 0, "description": "Ofis kullanımı"},
        ],
    },
    "STK-003": {
        "stock_id": "STK-003",
        "name": "Dell Latitude 5550 Laptop",
        "category": "equipment",
        "unit": "adet",
        "current_quantity": 3,
        "min_quantity": 1,
        "location": "Depo B",
        "movements": [
            {"id": "MOV-006", "type": "in", "date": "2026-05-02", "quantity": 5, "unit_cost": 42000.00, "description": "Teknosa alış INV-2026-004"},
            {"id": "MOV-007", "type": "out", "date": "2026-05-03", "quantity": 2, "unit_cost": 0, "description": "Çalışanlara teslim"},
        ],
    },
    "STK-004": {
        "stock_id": "STK-004",
        "name": "Samsung 27\" 4K Monitor",
        "category": "equipment",
        "unit": "adet",
        "current_quantity": 5,
        "min_quantity": 2,
        "location": "Depo B",
        "movements": [
            {"id": "MOV-008", "type": "in", "date": "2026-05-02", "quantity": 5, "unit_cost": 14500.00, "description": "Teknosa alış INV-2026-004"},
        ],
    },
    "STK-005": {
        "stock_id": "STK-005",
        "name": "Endüstriyel Temizlik Solüsyonu 5L",
        "category": "consumables",
        "unit": "adet",
        "current_quantity": 8,
        "min_quantity": 3,
        "location": "Depo A",
        "movements": [
            {"id": "MOV-009", "type": "in", "date": "2026-03-15", "quantity": 10, "unit_cost": 210.00, "description": "Toptan alış"},
            {"id": "MOV-010", "type": "in", "date": "2026-04-01", "quantity": 2, "unit_cost": 225.00, "description": "Migros alış INV-2026-001"},
            {"id": "MOV-011", "type": "out", "date": "2026-04-10", "quantity": 4, "unit_cost": 0, "description": "Ofis temizlik"},
        ],
    },
}

_movement_counter = 11


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _normalize_amount(value: object, default: Optional[float] = None) -> Optional[float]:
    if value is None:
        return default
    try:
        return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    except Exception:
        return default


# ---------------------------------------------------------------------------
# Core Stock Operations
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented stock listing with summary data
# for dashboard display.
def list_stocks() -> dict:
    summaries = []
    for item in MOCK_STOCK_DB.values():
        total_in = sum(m["quantity"] for m in item["movements"] if m["type"] == "in")
        total_out = sum(m["quantity"] for m in item["movements"] if m["type"] == "out")
        summaries.append({
            "stock_id": item["stock_id"],
            "name": item["name"],
            "category": item["category"],
            "unit": item["unit"],
            "current_quantity": item["current_quantity"],
            "min_quantity": item["min_quantity"],
            "location": item["location"],
            "total_in": total_in,
            "total_out": total_out,
            "low_stock": item["current_quantity"] <= item["min_quantity"],
        })
    return {"success": True, "count": len(summaries), "data": summaries}


def get_stock(stock_id: str) -> dict:
    item = MOCK_STOCK_DB.get(stock_id)
    if item is None:
        return {"success": False, "error": f"Stock '{stock_id}' not found."}
    return {"success": True, "data": deepcopy(item)}


# AI Traceability: Skills Agent implemented stock movement recording for
# deterministic in/out tracking.
def record_movement(stock_id: str, movement_type: str, quantity: int,
                    unit_cost: float, date: str, description: str = "") -> dict:
    global _movement_counter
    item = MOCK_STOCK_DB.get(stock_id)
    if item is None:
        return {"success": False, "error": f"Stock '{stock_id}' not found."}

    if movement_type not in ("in", "out"):
        return {"success": False, "error": "movement_type must be 'in' or 'out'."}

    if quantity <= 0:
        return {"success": False, "error": "quantity must be > 0."}

    if movement_type == "out" and quantity > item["current_quantity"]:
        return {"success": False, "error": f"Yetersiz stok. Mevcut: {item['current_quantity']}, İstenen: {quantity}"}

    _movement_counter += 1
    movement = {
        "id": f"MOV-{_movement_counter:03d}",
        "type": movement_type,
        "date": date,
        "quantity": quantity,
        "unit_cost": _normalize_amount(unit_cost, 0.0),
        "description": description,
    }

    item["movements"].append(movement)
    if movement_type == "in":
        item["current_quantity"] += quantity
    else:
        item["current_quantity"] -= quantity

    return {"success": True, "data": {"stock": deepcopy(item), "movement": movement}}


# ---------------------------------------------------------------------------
# FIFO / LIFO Valuation
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented FIFO and LIFO inventory valuation
# methods for accurate cost of goods sold (COGS) calculations.
def valuate_stock(stock_id: str, method: str = "fifo") -> dict:
    item = MOCK_STOCK_DB.get(stock_id)
    if item is None:
        return {"success": False, "error": f"Stock '{stock_id}' not found."}

    if method not in ("fifo", "lifo"):
        return {"success": False, "error": "method must be 'fifo' or 'lifo'."}

    # Build purchase lots (only 'in' movements with cost)
    lots = []
    for m in item["movements"]:
        if m["type"] == "in" and m["unit_cost"] > 0:
            lots.append({"date": m["date"], "quantity": m["quantity"], "unit_cost": m["unit_cost"]})

    # Calculate total sold
    total_out = sum(m["quantity"] for m in item["movements"] if m["type"] == "out")

    if method == "fifo":
        # FIFO: consume oldest lots first
        remaining_out = total_out
        cogs = 0.0
        fifo_lots = deepcopy(lots)
        for lot in fifo_lots:
            if remaining_out <= 0:
                break
            consumed = min(lot["quantity"], remaining_out)
            cogs += consumed * lot["unit_cost"]
            lot["quantity"] -= consumed
            remaining_out -= consumed

        # Remaining inventory value
        inv_value = sum(lot["quantity"] * lot["unit_cost"] for lot in fifo_lots)
    else:
        # LIFO: consume newest lots first
        remaining_out = total_out
        cogs = 0.0
        lifo_lots = deepcopy(lots)
        for lot in reversed(lifo_lots):
            if remaining_out <= 0:
                break
            consumed = min(lot["quantity"], remaining_out)
            cogs += consumed * lot["unit_cost"]
            lot["quantity"] -= consumed
            remaining_out -= consumed

        inv_value = sum(lot["quantity"] * lot["unit_cost"] for lot in lifo_lots)

    total_purchased = sum(lot["quantity"] * lot["unit_cost"] for lot in lots)

    return {
        "success": True,
        "data": {
            "stock_id": stock_id,
            "name": item["name"],
            "method": method.upper(),
            "current_quantity": item["current_quantity"],
            "total_purchased_value": _normalize_amount(total_purchased),
            "cost_of_goods_sold": _normalize_amount(cogs),
            "inventory_value": _normalize_amount(inv_value),
            "average_unit_cost": _normalize_amount(inv_value / item["current_quantity"]) if item["current_quantity"] > 0 else 0,
        },
    }
