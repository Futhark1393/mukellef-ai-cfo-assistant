from typing import Iterable


# ---------------------------------------------------------------------------
# Stock Grouping Helpers
# ---------------------------------------------------------------------------
# AI Traceability: Skills Agent added deterministic keyword-based grouping to
# classify OCR line items into stock categories for mock accounting payloads.
STOCK_GROUP_RULES: list[dict] = [
    {
        "key": "equipment",
        "label": "Equipment",
        "keywords": ["laptop", "monitor", "mouse", "keyboard", "dock", "server", "router", "switch", "printer"],
    },
    {
        "key": "consumables",
        "label": "Consumables",
        "keywords": ["paper", "cleaning", "toner", "coffee", "pantry", "cable", "supplies", "solution"],
    },
    {
        "key": "services",
        "label": "Services",
        "keywords": ["service", "subscription", "maintenance", "support", "saas", "cloud", "usage", "hosting"],
    },
    {
        "key": "inventory",
        "label": "Inventory",
        "keywords": ["fabric", "component", "spare", "bolt", "screw", "part", "material"],
    },
    {
        "key": "raw_materials",
        "label": "Raw Materials",
        "keywords": ["steel", "plastic", "resin", "chemical", "powder", "granule"],
    },
]


# AI Traceability: Skills Agent implemented deterministic classification to
# keep stock grouping outputs stable across runs.
def classify_line_item(description: str) -> str:
    text = (description or "").lower()
    for rule in STOCK_GROUP_RULES:
        if any(keyword in text for keyword in rule["keywords"]):
            return rule["key"]
    return "other"


# AI Traceability: Skills Agent implemented group summarization to prepare
# accounting-ready payloads with totals per stock category.
def group_line_items(line_items: Iterable[dict]) -> dict:
    groups: dict[str, dict] = {}

    def ensure_group(group_key: str) -> dict:
        if group_key not in groups:
            label = next((r["label"] for r in STOCK_GROUP_RULES if r["key"] == group_key), "Other")
            groups[group_key] = {
                "group_key": group_key,
                "group_label": label,
                "item_count": 0,
                "total_before_vat": 0.0,
                "total_vat": 0.0,
                "total_amount": 0.0,
                "line_items": [],
            }
        return groups[group_key]

    summary = {
        "total_before_vat": 0.0,
        "total_vat": 0.0,
        "total_amount": 0.0,
    }

    for item in line_items:
        group_key = classify_line_item(item.get("description", ""))
        group = ensure_group(group_key)
        line_total = float(item.get("line_total", 0.0) or 0.0)
        vat_amount = float(item.get("vat_amount", 0.0) or 0.0)
        quantity = float(item.get("quantity", 0.0) or 0.0)
        unit_price = float(item.get("unit_price", 0.0) or 0.0)
        total_before_vat = line_total - vat_amount if line_total else quantity * unit_price

        group["item_count"] += 1
        group["total_before_vat"] += total_before_vat
        group["total_vat"] += vat_amount
        group["total_amount"] += line_total
        group["line_items"].append(item)

        summary["total_before_vat"] += total_before_vat
        summary["total_vat"] += vat_amount
        summary["total_amount"] += line_total

    return {
        "groups": list(groups.values()),
        "summary": summary,
    }
