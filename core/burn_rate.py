# AI Traceability: Skills Agent developed this burn-rate and runway calculation module
# for retrospective cashflow analysis in the Mukellef - AI CFO Assistant.

import warnings
import statistics
from datetime import datetime, timedelta


def calculate_burn_rate(
    historical_data: list,
    method: str = "average",
) -> dict:
    """
    Calculate the monthly burn rate from historical cashflow records.

    Args:
        historical_data: A list of monthly records, each containing:
            - "month"   (str):  Label, e.g. "2026-01"
            - "revenue" (float): Total revenue for that month (>= 0)
            - "expense" (float): Total expenses for that month (>= 0)
        method: Aggregation strategy — "average", "weighted", or "median".

    Returns:
        A dict with gross_burn_rate, net_burn_rate, method,
        months_analyzed, and confidence level.

    Raises:
        ValueError: If historical_data is empty, a month label is missing,
                    or revenue is negative.
    """

    # --- Input validation ---
    # AI Traceability: Skills Agent added defensive checks for empty and malformed data.

    if not historical_data:
        raise ValueError("historical_data must contain at least one month of records.")

    if method not in ("average", "weighted", "median"):
        raise ValueError(f"method must be 'average', 'weighted', or 'median', got '{method}'")

    # --- Parse and validate each record ---
    # AI Traceability: Skills Agent implemented per-record validation with safe defaults for missing fields.

    monthly_expenses = []
    monthly_net_burns = []
    parsed_months = []

    for i, record in enumerate(historical_data):
        # Month label is required for traceability
        if "month" not in record:
            raise ValueError(f"Record at index {i} is missing the required 'month' key.")

        # Revenue defaults to 0.0 if missing, with a warning
        revenue = record.get("revenue")
        if revenue is None:
            warnings.warn(
                f"Record '{record['month']}': 'revenue' key missing, defaulting to 0.0.",
                UserWarning,
                stacklevel=2,
            )
            revenue = 0.0

        # Expense defaults to 0.0 if missing, with a warning
        expense = record.get("expense")
        if expense is None:
            warnings.warn(
                f"Record '{record['month']}': 'expense' key missing, defaulting to 0.0.",
                UserWarning,
                stacklevel=2,
            )
            expense = 0.0

        # Negative revenue is not valid in accounting
        if revenue < 0:
            raise ValueError(
                f"Record '{record['month']}': revenue cannot be negative, got {revenue}"
            )

        # Negative expense is not valid in accounting
        if expense < 0:
            raise ValueError(
                f"Record '{record['month']}': expense cannot be negative, got {expense}"
            )

        monthly_expenses.append(expense)
        monthly_net_burns.append(expense - revenue)
        parsed_months.append(record["month"])

    # --- Detect gaps in months ---
    # AI Traceability: Skills Agent added gap detection to warn about non-consecutive months.

    _detect_month_gaps(parsed_months)

    # --- Compute burn rates based on selected method ---
    # AI Traceability: Skills Agent implemented three aggregation strategies for flexibility.

    n = len(monthly_net_burns)

    if method == "average":
        gross_burn = sum(monthly_expenses) / n
        net_burn = sum(monthly_net_burns) / n

    elif method == "weighted":
        # Linear decay weights: most recent month gets highest weight
        weights = list(range(1, n + 1))
        total_weight = sum(weights)
        gross_burn = sum(e * w for e, w in zip(monthly_expenses, weights)) / total_weight
        net_burn = sum(b * w for b, w in zip(monthly_net_burns, weights)) / total_weight

    elif method == "median":
        gross_burn = statistics.median(monthly_expenses)
        net_burn = statistics.median(monthly_net_burns)

    # --- Determine confidence based on data volume ---
    # AI Traceability: Skills Agent added confidence scoring to reflect data reliability.

    if n >= 4:
        confidence = "high"
    elif n >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "gross_burn_rate": round(gross_burn, 2),
        "net_burn_rate": round(net_burn, 2),
        "method": method,
        "months_analyzed": n,
        "confidence": confidence,
    }


def calculate_runway(
    current_balance: float,
    burn_rate: float,
    min_runway_months: int = 3,
) -> dict:
    """
    Calculate how many months of runway remain at the given burn rate.

    Args:
        current_balance:   Cash on hand (can be negative = already in debt).
        burn_rate:         Net monthly burn (positive = losing money).
        min_runway_months: Threshold below which status becomes critical/warning.

    Returns:
        A dict with runway_months, runway_status, zero_cash_date,
        current_balance, and burn_rate.
    """

    # --- Input validation ---
    # AI Traceability: Skills Agent added guard for min_runway_months parameter.

    if not isinstance(min_runway_months, int) or min_runway_months < 1:
        raise ValueError(
            f"min_runway_months must be a positive integer, got {min_runway_months}"
        )

    # --- Handle already-depleted balance ---
    # AI Traceability: Skills Agent handles the edge case where the company is already in debt.

    if current_balance <= 0 and burn_rate > 0:
        return {
            "runway_months": 0,
            "runway_status": "critical",
            "zero_cash_date": "already_depleted",
            "current_balance": round(current_balance, 2),
            "burn_rate": round(burn_rate, 2),
        }

    # --- Handle profitable or break-even company ---
    # AI Traceability: Skills Agent handles infinite runway when net burn is zero or negative.

    if burn_rate <= 0:
        return {
            "runway_months": "infinite",
            "runway_status": "healthy",
            "zero_cash_date": None,
            "current_balance": round(current_balance, 2),
            "burn_rate": round(burn_rate, 2),
        }

    # --- Standard runway calculation ---
    # AI Traceability: Skills Agent computes runway as balance / burn and projects the zero-cash date.

    runway_months = current_balance / burn_rate

    # Determine status
    if runway_months < min_runway_months:
        status = "critical"
    elif runway_months < min_runway_months * 2:
        status = "warning"
    else:
        status = "healthy"

    # Project the date when cash hits zero
    today = datetime.now()
    zero_date = today + timedelta(days=runway_months * 30.44)  # Average days per month
    zero_cash_date = zero_date.strftime("%Y-%m")

    return {
        "runway_months": round(runway_months, 2),
        "runway_status": status,
        "zero_cash_date": zero_cash_date,
        "current_balance": round(current_balance, 2),
        "burn_rate": round(burn_rate, 2),
    }


def analyze_cashflow_health(
    historical_data: list,
    current_balance: float,
    method: str = "average",
    min_runway_months: int = 3,
) -> dict:
    """
    One-call entry point: computes burn rate + runway + status.

    Merges the outputs of calculate_burn_rate() and calculate_runway()
    into a single result dictionary.

    Args:
        historical_data:   List of monthly records (see calculate_burn_rate).
        current_balance:   Cash on hand.
        method:            Burn rate aggregation method.
        min_runway_months: Minimum months before status becomes critical.

    Returns:
        A merged dict combining burn rate metrics and runway analysis.
    """

    # AI Traceability: Skills Agent designed this convenience wrapper to simplify API usage.

    burn_result = calculate_burn_rate(historical_data, method=method)

    runway_result = calculate_runway(
        current_balance=current_balance,
        burn_rate=burn_result["net_burn_rate"],
        min_runway_months=min_runway_months,
    )

    # Merge both dictionaries, runway_result values take precedence for shared keys
    merged = {**burn_result, **runway_result}
    return merged


def _detect_month_gaps(months: list) -> None:
    """
    Emit a warning if month labels indicate non-consecutive months.

    Attempts to parse 'YYYY-MM' format; silently skips unparseable labels.
    """

    # AI Traceability: Skills Agent added internal helper for gap detection in historical data.

    parsed_dates = []
    for label in months:
        try:
            parsed_dates.append(datetime.strptime(label, "%Y-%m"))
        except (ValueError, TypeError):
            # Cannot parse this label — skip gap detection
            return

    if len(parsed_dates) < 2:
        return

    parsed_dates.sort()
    for i in range(1, len(parsed_dates)):
        diff_days = (parsed_dates[i] - parsed_dates[i - 1]).days
        # Allow 27-35 days to account for varying month lengths
        if diff_days < 27 or diff_days > 35:
            warnings.warn(
                f"Non-consecutive months detected between "
                f"'{months[i - 1]}' and '{months[i]}' ({diff_days} days gap). "
                f"Burn rate may be inaccurate.",
                UserWarning,
                stacklevel=3,
            )


# --- Quick smoke-test when the module is executed directly ---
if __name__ == "__main__":
    # AI Traceability: Skills Agent provided this demo block for quick validation.

    sample_data = [
        {"month": "2025-11", "revenue": 28_000.00, "expense": 35_000.00},
        {"month": "2025-12", "revenue": 31_000.00, "expense": 33_500.00},
        {"month": "2026-01", "revenue": 26_500.00, "expense": 34_000.00},
        {"month": "2026-02", "revenue": 29_000.00, "expense": 36_200.00},
        {"month": "2026-03", "revenue": 32_000.00, "expense": 34_800.00},
        {"month": "2026-04", "revenue": 27_500.00, "expense": 33_000.00},
    ]

    balance = 85_000.00

    print("Mukellef - AI CFO Assistant  |  Burn Rate & Runway Analysis")
    print("=" * 62)

    result = analyze_cashflow_health(sample_data, balance)

    print(f"  Method:            {result['method']}")
    print(f"  Months Analyzed:   {result['months_analyzed']}")
    print(f"  Confidence:        {result['confidence']}")
    print(f"  Gross Burn Rate:   TRY {result['gross_burn_rate']:>12,.2f}")
    print(f"  Net Burn Rate:     TRY {result['net_burn_rate']:>12,.2f}")
    print("-" * 62)
    print(f"  Current Balance:   TRY {result['current_balance']:>12,.2f}")
    print(f"  Runway:            {result['runway_months']} months")
    print(f"  Status:            {result['runway_status'].upper()}")
    print(f"  Zero Cash Date:    {result['zero_cash_date']}")
