# AI Traceability: Skills Agent developed the profitability analysis module
# for the Mukellef AI CFO Assistant.


# ---------------------------------------------------------------------------
# Mock Profitability Data
# ---------------------------------------------------------------------------
MOCK_PRODUCTS: list[dict] = [
    {
        "id": "PRD-001", "name": "Ürün A - Üretim",
        "type": "production",
        "revenue": 85000.00,
        "raw_material_cost": 32000.00,
        "labor_cost": 12000.00,
        "overhead_cost": 8000.00,
        "quantity_sold": 500,
    },
    {
        "id": "PRD-002", "name": "Ürün B - Ticaret",
        "type": "trade",
        "revenue": 62000.00,
        "purchase_cost": 45000.00,
        "shipping_cost": 3200.00,
        "quantity_sold": 200,
    },
    {
        "id": "PRD-003", "name": "Ürün C - Üretim",
        "type": "production",
        "revenue": 120000.00,
        "raw_material_cost": 48000.00,
        "labor_cost": 18000.00,
        "overhead_cost": 12000.00,
        "quantity_sold": 300,
    },
    {
        "id": "PRD-004", "name": "Ürün D - Ticaret",
        "type": "trade",
        "revenue": 38000.00,
        "purchase_cost": 28000.00,
        "shipping_cost": 1800.00,
        "quantity_sold": 150,
    },
]

MOCK_FIXED_COSTS = {
    "rent": 12000.00,
    "utilities": 3500.00,
    "insurance": 2800.00,
    "admin_salaries": 25000.00,
    "depreciation": 4500.00,
    "other": 2200.00,
}


# ---------------------------------------------------------------------------
# Core Profitability Analysis
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent implemented profitability analysis separating
# production vs trade products with proper COGS calculation.
def analyze_profitability() -> dict:
    production_items = []
    trade_items = []

    for p in MOCK_PRODUCTS:
        if p["type"] == "production":
            cogs = p["raw_material_cost"] + p["labor_cost"] + p["overhead_cost"]
            gross_profit = p["revenue"] - cogs
            margin = (gross_profit / p["revenue"] * 100) if p["revenue"] > 0 else 0
            production_items.append({
                "id": p["id"], "name": p["name"],
                "revenue": p["revenue"],
                "raw_material": p["raw_material_cost"],
                "labor": p["labor_cost"],
                "overhead": p["overhead_cost"],
                "cogs": round(cogs, 2),
                "gross_profit": round(gross_profit, 2),
                "margin_pct": round(margin, 2),
                "unit_profit": round(gross_profit / p["quantity_sold"], 2) if p["quantity_sold"] > 0 else 0,
            })
        else:
            cogs = p["purchase_cost"] + p.get("shipping_cost", 0)
            gross_profit = p["revenue"] - cogs
            margin = (gross_profit / p["revenue"] * 100) if p["revenue"] > 0 else 0
            trade_items.append({
                "id": p["id"], "name": p["name"],
                "revenue": p["revenue"],
                "purchase_cost": p["purchase_cost"],
                "shipping_cost": p.get("shipping_cost", 0),
                "cogs": round(cogs, 2),
                "gross_profit": round(gross_profit, 2),
                "margin_pct": round(margin, 2),
                "unit_profit": round(gross_profit / p["quantity_sold"], 2) if p["quantity_sold"] > 0 else 0,
            })

    total_revenue = sum(p["revenue"] for p in MOCK_PRODUCTS)
    total_cogs_prod = sum(i["cogs"] for i in production_items)
    total_cogs_trade = sum(i["cogs"] for i in trade_items)
    total_cogs = total_cogs_prod + total_cogs_trade
    total_gross_profit = total_revenue - total_cogs
    total_fixed = sum(MOCK_FIXED_COSTS.values())
    net_profit = total_gross_profit - total_fixed

    # Kar vs Karlılık (Rantabilite)
    total_capital = 500000.00  # Mock equity
    rantabilite = (net_profit / total_capital * 100) if total_capital > 0 else 0

    return {
        "success": True,
        "data": {
            "production": production_items,
            "trade": trade_items,
            "fixed_costs": MOCK_FIXED_COSTS,
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "total_cogs": round(total_cogs, 2),
                "gross_profit": round(total_gross_profit, 2),
                "gross_margin_pct": round((total_gross_profit / total_revenue * 100) if total_revenue > 0 else 0, 2),
                "total_fixed_costs": round(total_fixed, 2),
                "net_profit": round(net_profit, 2),
                "net_margin_pct": round((net_profit / total_revenue * 100) if total_revenue > 0 else 0, 2),
                "rantabilite_pct": round(rantabilite, 2),
                "total_capital": total_capital,
            },
        },
    }
