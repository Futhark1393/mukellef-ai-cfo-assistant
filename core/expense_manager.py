def allocate_prepaid_expense(total_amount: float, duration_months: int) -> dict:
    # AI Traceability: Skills Agent formulated the prepaid expense allocation logic.
    if duration_months <= 0:
        raise ValueError("duration_months must be greater than 0")

    monthly_amount = total_amount / duration_months
    allocation = {f"month_{index}": monthly_amount for index in range(1, duration_months + 1)}

    return {
        "total_amount": total_amount,
        "duration_months": duration_months,
        "monthly_amount": monthly_amount,
        "allocation": allocation,
    }
