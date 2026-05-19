import pandas as pd

from functions import (
    convert_to_monthly_amount,
    simulate_retirement_phase,
    simulate_savings_phase,
)


def test_convert_to_monthly_amount():
    assert convert_to_monthly_amount(1000, "Monthly") == 1000
    assert round(convert_to_monthly_amount(12000, "Yearly"), 2) == 1000.00


def test_savings_phase_with_expense():
    expenses = pd.DataFrame(
        {
            "month": [2],
            "amount": [500],
            "label": ["Test expense"],
        }
    )

    result = simulate_savings_phase(
        starting_balance=1000,
        annual_interest_rate=0,
        regular_contribution=100,
        contribution_frequency="Monthly",
        duration_months=3,
        one_off_expenses=expenses,
    )

    assert len(result) == 3
    assert result["ending_balance"].iloc[-1] == 800


def test_retirement_phase_stops_at_zero():
    result = simulate_retirement_phase(
        starting_balance=1000,
        annual_interest_rate=0,
        regular_spending=600,
        spending_frequency="Monthly",
        max_months=10,
    )

    assert len(result) == 2
    assert result["ending_balance"].iloc[-1] == 0