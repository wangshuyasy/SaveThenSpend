from __future__ import annotations

from typing import Literal

import pandas as pd


Frequency = Literal["Weekly", "Bi-weekly", "Monthly", "Yearly"]


def convert_to_monthly_amount(amount: float, frequency: Frequency) -> float:
    """
    Convert a regular contribution or spending amount into an estimated monthly amount.

    Args:
        amount: The amount paid or received per selected frequency.
        frequency: The frequency of the amount.

    Returns:
        The equivalent monthly amount.
    """
    if amount < 0:
        raise ValueError("Amount cannot be negative.")

    conversion = {
        "Weekly": 52 / 12,
        "Bi-weekly": 26 / 12,
        "Monthly": 1,
        "Yearly": 1 / 12,
    }

    return amount * conversion[frequency]


def normalise_expenses(expenses_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate the one-off expenses table.

    Args:
        expenses_df: A DataFrame with month, amount, and label columns.

    Returns:
        A cleaned DataFrame containing valid expenses only.
    """
    required_columns = {"month", "amount", "label"}

    if expenses_df.empty:
        return pd.DataFrame(columns=["month", "amount", "label"])

    if not required_columns.issubset(expenses_df.columns):
        raise ValueError("Expenses table must contain month, amount, and label columns.")

    cleaned = expenses_df.copy()
    cleaned["month"] = pd.to_numeric(cleaned["month"], errors="coerce")
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
    cleaned["label"] = cleaned["label"].fillna("One-off expense").astype(str)

    cleaned = cleaned.dropna(subset=["month", "amount"])
    cleaned = cleaned[(cleaned["month"] >= 1) & (cleaned["amount"] > 0)]

    cleaned["month"] = cleaned["month"].astype(int)

    return cleaned[["month", "amount", "label"]]


def simulate_savings_phase(
    starting_balance: float,
    annual_interest_rate: float,
    regular_contribution: float,
    contribution_frequency: Frequency,
    duration_months: int,
    one_off_expenses: pd.DataFrame,
) -> pd.DataFrame:
    """
    Simulate the savings phase month by month.

    Each month applies interest, adds regular contributions, subtracts scheduled
    one-off expenses, and records the ending balance.

    Args:
        starting_balance: Initial amount of money available.
        annual_interest_rate: Expected annual interest rate as a percentage.
        regular_contribution: Regular saving amount.
        contribution_frequency: Frequency of the regular saving amount.
        duration_months: Number of months to simulate.
        one_off_expenses: DataFrame containing month, amount, and label columns.

    Returns:
        A DataFrame containing the monthly savings timeline.
    """
    if starting_balance < 0:
        raise ValueError("Starting balance cannot be negative.")

    if duration_months <= 0:
        raise ValueError("Duration must be greater than zero.")

    monthly_interest_rate = annual_interest_rate / 100 / 12
    monthly_contribution = convert_to_monthly_amount(
        regular_contribution,
        contribution_frequency,
    )

    expenses = normalise_expenses(one_off_expenses)
    balance = starting_balance
    records = []

    for month in range(1, duration_months + 1):
        interest = balance * monthly_interest_rate
        balance += interest
        balance += monthly_contribution

        monthly_expenses = expenses[expenses["month"] == month]
        expense_total = float(monthly_expenses["amount"].sum())

        balance -= expense_total

        records.append(
            {
                "phase": "Savings",
                "month": month,
                "starting_balance": round(balance - interest - monthly_contribution + expense_total, 2),
                "interest": round(interest, 2),
                "contribution": round(monthly_contribution, 2),
                "expense": round(expense_total, 2),
                "spending": 0.0,
                "ending_balance": round(balance, 2),
            }
        )

    return pd.DataFrame(records)


def simulate_retirement_phase(
    starting_balance: float,
    annual_interest_rate: float,
    regular_spending: float,
    spending_frequency: Frequency,
    annual_inflation_rate: float,
    max_months: int,
) -> pd.DataFrame:
    """
    Simulate the retirement drawdown phase month by month.

    Each month applies interest, subtracts regular spending, and records the
    ending balance. The simulation stops early if the balance reaches zero.

    Args:
        starting_balance: Initial retirement balance.
        annual_interest_rate: Expected annual interest rate as a percentage.
        regular_spending: Regular spending amount.
        spending_frequency: Frequency of the spending amount.
        max_months: Maximum number of months to simulate.

    Returns:
        A DataFrame containing the monthly retirement timeline.
    """
    if starting_balance < 0:
        raise ValueError("Starting balance cannot be negative.")

    if max_months <= 0:
        raise ValueError("Maximum months must be greater than zero.")

    monthly_interest_rate = annual_interest_rate / 100 / 12
    monthly_spending = convert_to_monthly_amount(regular_spending, spending_frequency)
    monthly_inflation_rate = annual_inflation_rate / 100 / 12

    balance = starting_balance
    records = []

    for month in range(1, max_months + 1):
        starting_month_balance = balance
        interest = balance * monthly_interest_rate
        balance += interest
        inflation_adjusted_spending = monthly_spending * (
            (1 + monthly_inflation_rate) ** (month - 1)
        )
        balance -= inflation_adjusted_spending

        if balance < 0:
            balance = 0

        records.append(
            {
                "phase": "Retirement",
                "month": month,
                "starting_balance": round(starting_month_balance, 2),
                "interest": round(interest, 2),
                "contribution": 0.0,
                "expense": 0.0,
                "spending": round(inflation_adjusted_spending, 2),
                "ending_balance": round(balance, 2),
            }
        )

        if balance <= 0:
            break

    return pd.DataFrame(records)


def combine_timelines(
    savings_df: pd.DataFrame | None,
    retirement_df: pd.DataFrame | None,
) -> pd.DataFrame:
    """
    Combine savings and retirement timelines into one continuous timeline.

    Args:
        savings_df: Savings phase DataFrame, or None.
        retirement_df: Retirement phase DataFrame, or None.

    Returns:
        A combined DataFrame with a continuous display month.
    """
    frames = []

    if savings_df is not None and not savings_df.empty:
        frames.append(savings_df)

    if retirement_df is not None and not retirement_df.empty:
        retirement_copy = retirement_df.copy()
        offset = len(savings_df) if savings_df is not None else 0
        retirement_copy["month"] = retirement_copy["month"] + offset
        frames.append(retirement_copy)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    combined["display_year"] = (combined["month"] / 12).round(2)

    return combined


def generate_summary(timeline_df: pd.DataFrame) -> dict[str, float | int | str]:
    """
    Generate high-level summary metrics from a financial timeline.

    Args:
        timeline_df: Combined monthly timeline.

    Returns:
        A dictionary of summary metrics.
    """
    if timeline_df.empty:
        return {
            "final_balance": 0.0,
            "total_months": 0,
            "retirement_months_supported": 0,
            "retirement_years_supported": 0.0,
            "lowest_balance": 0.0,
            "highest_balance": 0.0,
            "status": "No simulation generated",
        }

    final_balance = float(timeline_df["ending_balance"].iloc[-1])
    savings_df = timeline_df[timeline_df["phase"] == "Savings"]
    savings_months = len(savings_df)
    savings_years = savings_months / 12

    retirement_df = timeline_df[timeline_df["phase"] == "Retirement"]
    retirement_months_supported = len(retirement_df)
    retirement_years_supported = retirement_months_supported / 12

    status = "Positive"
    if final_balance <= 0:
        status = "Depleted"

    return {
        "final_balance": round(final_balance, 2),
        "years_spent_saving": round(savings_years, 2),
        "retirement_years_supported": round(retirement_years_supported, 2),
        "lowest_balance": round(float(timeline_df["ending_balance"].min()), 2),
        "highest_balance": round(float(timeline_df["ending_balance"].max()), 2),
        "status": status,
    }