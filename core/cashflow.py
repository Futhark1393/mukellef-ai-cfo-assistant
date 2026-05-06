# AI Traceability: Skills Agent developed this 6-month cashflow projection algorithm based on monthly burn rates.
# This module provides cashflow prediction functionality for the Mukellef - AI CFO Assistant.


def predict_cashflow(
    current_balance: float,
    monthly_revenue: float,
    monthly_expense: float,
    months: int = 6,
) -> list:
    """
    Calculate the projected running balance for each future month.

    The projection applies a simple linear model: for each month the net
    cashflow (revenue minus expenses) is added to the running balance.

    Args:
        current_balance: The starting cash balance (can be negative if the
                         company is already in deficit).
        monthly_revenue: Expected average monthly revenue. Must be >= 0.
        monthly_expense: Expected average monthly expense. Must be >= 0.
        months:          Number of months to project (default 6). Must be >= 1.

    Returns:
        A list of dictionaries, each containing:
            - 'month':              A human-readable label (e.g. 'Month 1').
            - 'projected_balance':  The projected balance at the end of that
                                    month, rounded to two decimal places.

    Raises:
        ValueError: If monthly_revenue or monthly_expense is negative,
                    or if months is less than 1.
    """

    # --- Input validation ---
    # AI Traceability: Skills Agent added defensive checks for edge-case inputs.

    if monthly_revenue < 0:
        raise ValueError(
            f"monthly_revenue must be >= 0, got {monthly_revenue}"
        )

    if monthly_expense < 0:
        raise ValueError(
            f"monthly_expense must be >= 0, got {monthly_expense}"
        )

    if not isinstance(months, int) or months < 1:
        raise ValueError(
            f"months must be a positive integer, got {months}"
        )

    # --- Projection calculation ---
    # AI Traceability: Skills Agent designed this linear projection loop
    # using a constant net-cashflow (revenue - expense) applied each month.

    # Net monthly cashflow (positive = surplus, negative = burn)
    net_monthly_cashflow: float = monthly_revenue - monthly_expense

    projections: list = []
    running_balance: float = current_balance

    for month_number in range(1, months + 1):
        # Accumulate the net cashflow for the current month
        running_balance += net_monthly_cashflow

        projections.append(
            {
                "month": f"Month {month_number}",
                "projected_balance": round(running_balance, 2),
            }
        )

    return projections


# --- Quick smoke-test when the module is executed directly ---
if __name__ == "__main__":
    # AI Traceability: Skills Agent provided this demo block for quick validation.
    sample = predict_cashflow(
        current_balance=100_000.0,
        monthly_revenue=30_000.0,
        monthly_expense=25_000.0,
        months=6,
    )

    print("Mukellef - AI CFO Assistant  |  6-Month Cashflow Projection")
    print("=" * 60)
    for entry in sample:
        balance = entry["projected_balance"]
        print(f"  {entry['month']:>10}  ->  TRY {balance:>12,.2f}")
