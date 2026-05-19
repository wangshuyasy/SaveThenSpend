from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from functions import (
    combine_timelines,
    generate_summary,
    simulate_retirement_phase,
    simulate_savings_phase,
)


st.set_page_config(
    page_title="SaveThenSpend",
    page_icon="💰",
    layout="wide",
)


st.title("SaveThenSpend")
st.caption("A two-phase savings and retirement simulator built with Python and Streamlit.")


with st.sidebar:
    st.header("Simulation Settings")

    enable_savings = st.toggle("Enable savings phase", value=True)
    enable_retirement = st.toggle("Enable retirement phase", value=True)

    use_savings_for_retirement = False
    if enable_savings and enable_retirement:
        use_savings_for_retirement = st.toggle(
            "Use final savings balance for retirement",
            value=True,
        )


savings_df = None
retirement_df = None
final_savings_balance = 0.0


if enable_savings:
    st.subheader("Part 1: Savings Phase")

    col1, col2, col3 = st.columns(3)

    with col1:
        starting_balance = st.number_input(
            "Starting savings balance",
            min_value=0.0,
            value=5000.0,
            step=500.0,
        )

        savings_interest_rate = st.number_input(
            "Annual interest rate (%)",
            min_value=-20.0,
            max_value=80.0,
            value=5.5,
            step=0.25,
        )

    with col2:
        regular_contribution = st.number_input(
            "Regular contribution amount",
            min_value=0.0,
            value=2000.0,
            step=50.0,
        )

        contribution_frequency = st.selectbox(
            "Contribution frequency",
            ["Weekly", "Bi-weekly", "Monthly", "Yearly"],
            index=2,
        )

    with col3:
        savings_duration_months = st.number_input(
            "Savings duration in months",
            min_value=1,
            value=24,
            step=1,
        )

    st.markdown("#### One-off expenses during savings phase")

    default_expenses = pd.DataFrame(
        {
            "month": [12, 24],
            "amount": [8000.0, 5000.0],
            "label": [
                "Tuition payment",
                "Tuition payment",
            ],
        }
    )

    one_off_expenses = st.data_editor(
        default_expenses,
        num_rows="dynamic",
        width='stretch',
        column_config={
            "month": st.column_config.NumberColumn(
                "Month",
                min_value=1,
                step=1,
                help="The month when the one-off expense occurs.",
            ),
            "amount": st.column_config.NumberColumn(
                "Amount",
                min_value=0.0,
                step=100.0,
                help="The amount deducted from savings.",
            ),
            "label": st.column_config.TextColumn(
                "Label",
                help="Short description of the expense.",
            ),
        },
    )

    savings_df = simulate_savings_phase(
        starting_balance=starting_balance,
        annual_interest_rate=savings_interest_rate,
        regular_contribution=regular_contribution,
        contribution_frequency=contribution_frequency,
        duration_months=int(savings_duration_months),
        one_off_expenses=one_off_expenses,
    )

    final_savings_balance = float(savings_df["ending_balance"].iloc[-1])

    st.metric("Final savings balance", f"${final_savings_balance:,.2f}")


if enable_retirement:
    st.subheader("Part 2: Retirement Drawdown Phase")

    col1, col2, col3 = st.columns(3)

    with col1:
        if use_savings_for_retirement and enable_savings:
            retirement_starting_balance = final_savings_balance
            st.number_input(
                "Starting retirement balance",
                value=retirement_starting_balance,
                disabled=True,
            )
        else:
            retirement_starting_balance = st.number_input(
                "Starting retirement balance",
                min_value=0.0,
                value=100000.0,
                step=1000.0,
            )

    with col2:
        retirement_interest_rate = st.number_input(
            "Retirement annual interest rate (%)",
            min_value=-20.0,
            max_value=50.0,
            value=3.0,
            step=0.25,
        )

        regular_spending = st.number_input(
            "Regular spending amount",
            min_value=0.0,
            value=2500.0,
            step=100.0,
        )

        inflation_rate = st.number_input(
            "Annual inflation rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=2.5,
            step=0.1,
        )

    with col3:
        spending_frequency = st.selectbox(
            "Spending frequency",
            ["Weekly", "Bi-weekly", "Monthly", "Yearly"],
            index=2,
        )

        retirement_max_months = st.number_input(
            "Maximum retirement duration in months",
            min_value=1,
            value=360,
            step=12,
        )

    if use_savings_for_retirement and enable_savings and final_savings_balance <= 0:
        st.warning(
            "Savings balance is zero or negative, so retirement simulation cannot start from savings result."
        )
        retirement_df = None
    else:
        retirement_df = simulate_retirement_phase(
            starting_balance=retirement_starting_balance,
            annual_interest_rate=retirement_interest_rate,
            regular_spending=regular_spending,
            spending_frequency=spending_frequency,
            annual_inflation_rate=inflation_rate,
            max_months=int(retirement_max_months),
        )


timeline_df = combine_timelines(savings_df, retirement_df)
summary = generate_summary(timeline_df)


st.subheader("Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Final balance", f"${summary['final_balance']:,.2f}")
col2.metric("Years spent saving", f"{summary['years_spent_saving']}")
col3.metric(
    "Retirement years supported",
    f"{summary['retirement_years_supported']}",
)
col4.metric("Status", str(summary["status"]))


if not timeline_df.empty:
    st.subheader("Balance Timeline")

    fig = px.line(
        timeline_df,
        x="month",
        y="ending_balance",
        color="phase",
        markers=True,
        title="Balance over Time",
        labels={
            "month": "Month",
            "ending_balance": "Ending Balance",
            "phase": "Phase",
        },
    )

    st.plotly_chart(
        fig,
        config={"responsive": True,
                "width": "stretch",}
    )

    st.subheader("Monthly Simulation Table")

    st.dataframe(
        timeline_df,
        width='stretch',
        hide_index=True,
    )
else:
    st.info("Enable at least one phase to generate a simulation.")