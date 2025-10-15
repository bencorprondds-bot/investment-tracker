# Wealthfolio

Wealthfolio is a lightweight personal investment tracker that helps you understand how your
portfolio is performing. It ships with a simple command line interface, reusable Python library
components, and a set of sample data so you can get started immediately.

## Features

- Model transactions and holdings for equities and funds.
- Compute portfolio level metrics such as market value, invested capital, and unrealized gain.
- Render human-readable summaries and holdings tables for quick reporting.
- Command line interface with JSON-based import for transactions and prices.

## Getting started

Wealthfolio is built with Python 3.11+. Create a virtual environment and install the project in
editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run the CLI with the bundled sample data:

```bash
wealthfolio --table
```

You can also specify your own JSON files:

```bash
wealthfolio --transactions my_transactions.json --prices my_prices.json --table
```

Transactions should be a list of objects with the fields `symbol`, `quantity`, `price`, `date`, and
an optional `type` (`BUY` or `SELL`). Prices should be a JSON object mapping ticker symbols to the
latest price.

## Running tests

We use `pytest` for automated tests:

```bash
pip install -e .[test]
pytest
```

Alternatively, install the development dependencies manually and run `pytest` from the repository
root.
