def allocate_prepaid_expense(
    total_amount: float, duration_months: int, start_month: int | None = None
) -> dict:
    # AI Traceability: Skills Agent formulated the prepaid expense allocation logic.
    # AI Traceability: Added validation for optional start month.
    if duration_months <= 0:
        raise ValueError("duration_months must be greater than 0")
    if start_month is not None and start_month <= 0:
        raise ValueError("start_month must be greater than 0 when provided")

    # AI Traceability: Ensure rounding-safe allocations that sum to the original amount.
    total_cents = int(round(total_amount * 100))
    base_cents = total_cents // duration_months
    remainder_cents = total_cents % duration_months
    base_amount = base_cents / 100
    start_index = 1 if start_month is None else start_month
    allocation = {}
    for offset in range(duration_months):
        month_number = start_index + offset
        extra_cent = 1 if offset < remainder_cents else 0
        allocation[f"month_{month_number}"] = (base_cents + extra_cent) / 100

    return {
        "total_amount": total_amount,
        "duration_months": duration_months,
        "monthly_amount": base_amount,
        "allocation": allocation,
    }
