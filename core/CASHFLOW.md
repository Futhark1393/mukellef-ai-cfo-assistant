# Cashflow Module

## Purpose
Provide a simple 6-month cashflow projection to help founders understand runway risk and monthly balance trends.

## Logic
Uses a linear projection: net monthly cashflow (monthly revenue minus monthly expense) is added to the running balance for each month. Each month is emitted as a labeled entry with the projected balance rounded to two decimals.

## Inputs/Outputs
- Inputs
  - `current_balance` (float): starting cash balance.
  - `monthly_revenue` (float): expected average monthly revenue.
  - `monthly_expense` (float): expected average monthly expense.
  - `months` (int, default 6): number of months to project.
- Output
  - `list[dict]` with entries like:
    - `{"month": "Month 1", "projected_balance": 105000.0}`

Example
```
Input: current_balance=100000, monthly_revenue=30000, monthly_expense=25000, months=3
Output: [
  {"month": "Month 1", "projected_balance": 105000.0},
  {"month": "Month 2", "projected_balance": 110000.0},
  {"month": "Month 3", "projected_balance": 115000.0}
]
```

## AI Traceability
This module was architected with AI assistance to accelerate rapid prototyping and ensure consistent validation logic.
