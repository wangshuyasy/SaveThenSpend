# SaveThenSpend

SaveThenSpend is a Python Streamlit app that simulates two financial stages:

- saving
- retirement spending.

## Description

SaveThenSpend is a financial planning simulator designed for individuals who want to better understand their long-term savings and spending habits. The program allows users to simulate both a savings phase and a retirement spending phase using compound interest, regular contributions, and one-off expenses such as tuition fees. Users can estimate how their savings grow over time and how long their funds may last during retirement.

The target audience includes any individual who is interested in financial independence or early retirement (FIRE). The tool hopes to encourage realistic financial planning, promote healthy saving habits, and awareness of financial sustainability.

### Try it out! It is live at [savethenspend.streamlit.app](https://savethenspend.streamlit.app)

## Features

- Savings simulation with compound interest
- Supports regular contribution, one-off expenses, such as school fee payments
- Retirement drawdown simulation
- Option to pass final savings balance into retirement phase
- Provides balance charts and summary table

## Advanced Topics Used

1. Break
2. Raise
3. Testing

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Running the app:

```bash
streamlit run app.py
```

## Testing

Run tests with pytest:

```bash
pytest test_functions.py
```