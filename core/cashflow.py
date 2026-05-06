# AI Traceability: Skills Agent developed this 6-month cashflow projection algorithm based on monthly burn rates.
# AI Traceability: Skills Agent enhanced this module with multi-scenario projections (best/base/worst),
# revenue growth rate modelling, cumulative net-cashflow tracking, and strengthened input validation.
# This module provides cashflow prediction functionality for the Mukellef - AI CFO Assistant.

import math


# ---------------------------------------------------------------------------
# Primary projection function
# ---------------------------------------------------------------------------

def predict_cashflow(
    current_balance: float,
    monthly_revenue: float,
    monthly_expense: float,
    months: int = 6,
    revenue_growth_rate: float = 0.0,
    expense_growth_rate: float = 0.0,
) -> list:
    """
    Calculate the projected running balance for each future month.

    Supports an optional monthly growth rate for both revenue and expenses
    so that projections reflect realistic trends instead of flat-line
    assumptions.

    Args:
        current_balance:     The starting cash balance (can be negative if the
                             company is already in deficit).
        monthly_revenue:     Expected average monthly revenue. Must be >= 0.
        monthly_expense:     Expected average monthly expense. Must be >= 0.
        months:              Number of months to project (default 6, max 24).
                             Must be >= 1.
        revenue_growth_rate: Monthly compounding growth rate for revenue
                             (e.g. 0.05 = 5 % MoM growth). Default 0.0.
        expense_growth_rate: Monthly compounding growth rate for expenses
                             (e.g. 0.02 = 2 % MoM increase). Default 0.0.

    Returns:
        A list of dictionaries, each containing:
            - 'month':              Human-readable label (e.g. 'Month 1').
            - 'projected_balance':  Running balance at end of month (2 dp).
            - 'revenue':            Revenue applied in that month (2 dp).
            - 'expense':            Expense applied in that month (2 dp).
            - 'net_cashflow':       Revenue minus expense for that month (2 dp).
            - 'cumulative_net':     Total net cashflow since Month 1 (2 dp).

    Raises:
        ValueError: On invalid or missing inputs.
    """

    # --- Input validation ---
    # AI Traceability: Skills Agent strengthened validation to cover None, NaN,
    # non-numeric types, and capped the projection window at 24 months.

    _validate_numeric("current_balance", current_balance)
    _validate_non_negative("monthly_revenue", monthly_revenue)
    _validate_non_negative("monthly_expense", monthly_expense)
    _validate_numeric("revenue_growth_rate", revenue_growth_rate)
    _validate_numeric("expense_growth_rate", expense_growth_rate)

    if not isinstance(months, int) or months < 1:
        raise ValueError(f"months must be a positive integer, got {months}")
    if months > 24:
        raise ValueError(f"months must be <= 24 to keep projections meaningful, got {months}")

    # --- Projection calculation ---
    # AI Traceability: Skills Agent designed this growth-aware projection loop.
    # Revenue and expense each compound independently at their given growth rate
    # before being applied to the running balance.

    projections: list = []
    running_balance: float = current_balance
    cumulative_net: float = 0.0
    current_revenue: float = monthly_revenue
    current_expense: float = monthly_expense

    for month_number in range(1, months + 1):
        # Apply compounding growth starting from month 2
        if month_number > 1:
            current_revenue *= (1 + revenue_growth_rate)
            current_expense *= (1 + expense_growth_rate)

        net = current_revenue - current_expense
        running_balance += net
        cumulative_net += net

        projections.append({
            "month": f"Month {month_number}",
            "projected_balance": round(running_balance, 2),
            "revenue": round(current_revenue, 2),
            "expense": round(current_expense, 2),
            "net_cashflow": round(net, 2),
            "cumulative_net": round(cumulative_net, 2),
        })

    return projections


# ---------------------------------------------------------------------------
# Multi-scenario analysis
# ---------------------------------------------------------------------------

# AI Traceability: Skills Agent created this scenario analysis function to provide
# best-case, base-case, and worst-case projections for decision-makers.

def predict_cashflow_scenarios(
    current_balance: float,
    monthly_revenue: float,
    monthly_expense: float,
    months: int = 6,
    optimistic_revenue_growth: float = 0.05,
    pessimistic_revenue_growth: float = -0.05,
    pessimistic_expense_growth: float = 0.03,
) -> dict:
    """
    Generate best / base / worst case cashflow projections.

    Args:
        current_balance:             Starting cash balance.
        monthly_revenue:             Baseline monthly revenue.
        monthly_expense:             Baseline monthly expense.
        months:                      Projection window (default 6).
        optimistic_revenue_growth:   Revenue growth for best case (default +5 %).
        pessimistic_revenue_growth:  Revenue growth for worst case (default -5 %).
        pessimistic_expense_growth:  Expense growth for worst case (default +3 %).

    Returns:
        A dict with keys 'best_case', 'base_case', 'worst_case',
        each containing the list returned by predict_cashflow(),
        plus a 'summary' key with final balances for quick comparison.
    """

    # Best case: revenue grows, expenses stay flat
    best = predict_cashflow(
        current_balance, monthly_revenue, monthly_expense, months,
        revenue_growth_rate=optimistic_revenue_growth,
        expense_growth_rate=0.0,
    )

    # Base case: everything stays flat
    base = predict_cashflow(
        current_balance, monthly_revenue, monthly_expense, months,
        revenue_growth_rate=0.0,
        expense_growth_rate=0.0,
    )

    # Worst case: revenue shrinks, expenses grow
    worst = predict_cashflow(
        current_balance, monthly_revenue, monthly_expense, months,
        revenue_growth_rate=pessimistic_revenue_growth,
        expense_growth_rate=pessimistic_expense_growth,
    )

    # AI Traceability: Skills Agent added a summary block so callers can quickly
    # compare final projected balances across all three scenarios.

    summary = {
        "best_case_final_balance": best[-1]["projected_balance"],
        "base_case_final_balance": base[-1]["projected_balance"],
        "worst_case_final_balance": worst[-1]["projected_balance"],
        "months_projected": months,
    }

    return {
        "best_case": best,
        "base_case": base,
        "worst_case": worst,
        "summary": summary,
    }


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

# AI Traceability: Skills Agent extracted validation into reusable helpers
# to ensure consistent checks across all public functions.

def _validate_numeric(name: str, value) -> None:
    """Raise ValueError if value is None, not a number, or NaN."""
    if value is None:
        raise ValueError(f"{name} is required and cannot be None.")
    if not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number, got {type(value).__name__}.")
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{name} must be a finite number, got {value}.")


def _validate_non_negative(name: str, value) -> None:
    """Validate that value is numeric AND >= 0."""
    _validate_numeric(name, value)
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value}.")


# ---------------------------------------------------------------------------
# Quick smoke-test when the module is executed directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # AI Traceability: Skills Agent provided this demo block for quick validation.

    print("=" * 65)
    print("  Mukellef - AI CFO Assistant  |  Enhanced Cashflow Projection")
    print("=" * 65)

    # --- Base projection with 3% revenue growth ---
    print("\n[ Base Projection — 3% MoM Revenue Growth ]")
    result = predict_cashflow(
        current_balance=100_000.0,
        monthly_revenue=30_000.0,
        monthly_expense=25_000.0,
        months=6,
        revenue_growth_rate=0.03,
    )
    print(f"  {'Month':<10} {'Revenue':>12} {'Expense':>12} {'Net':>12} {'Balance':>14}")
    print("  " + "-" * 62)
    for e in result:
        print(
            f"  {e['month']:<10} "
            f"TRY {e['revenue']:>9,.2f} "
            f"TRY {e['expense']:>9,.2f} "
            f"TRY {e['net_cashflow']:>9,.2f} "
            f"TRY {e['projected_balance']:>11,.2f}"
        )

    # --- Scenario analysis ---
    print("\n[ Scenario Analysis — Best / Base / Worst ]")
    scenarios = predict_cashflow_scenarios(
        current_balance=100_000.0,
        monthly_revenue=30_000.0,
        monthly_expense=25_000.0,
        months=6,
    )
    s = scenarios["summary"]
    print(f"  Best-case  final balance:  TRY {s['best_case_final_balance']:>12,.2f}")
    print(f"  Base-case  final balance:  TRY {s['base_case_final_balance']:>12,.2f}")
    print(f"  Worst-case final balance:  TRY {s['worst_case_final_balance']:>12,.2f}")
