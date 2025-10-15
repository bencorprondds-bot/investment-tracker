from __future__ import annotations

import json
from datetime import date

import pytest

from wealthfolio.cli import main as cli_main
from wealthfolio.portfolio import Portfolio, Transaction
from wealthfolio.providers import MarketDataProvider
from wealthfolio.report import generate_summary, holdings_table


@pytest.fixture()
def sample_transactions() -> list[Transaction]:
    return [
        Transaction(symbol="AAPL", quantity=5, price=150, timestamp=date(2023, 1, 15), type="BUY"),
        Transaction(symbol="AAPL", quantity=2, price=160, timestamp=date(2023, 3, 10), type="BUY"),
        Transaction(symbol="TSLA", quantity=1, price=700, timestamp=date(2022, 12, 1), type="BUY"),
        Transaction(symbol="TSLA", quantity=0.5, price=800, timestamp=date(2023, 7, 1), type="SELL"),
        Transaction(symbol="VTI", quantity=10, price=200, timestamp=date(2023, 2, 1), type="BUY"),
    ]


@pytest.fixture()
def sample_provider() -> MarketDataProvider:
    return MarketDataProvider({"AAPL": 195.25, "TSLA": 250.10, "VTI": 210.75})


def test_transaction_validation() -> None:
    with pytest.raises(ValueError):
        Transaction(symbol="AAPL", quantity=-1, price=100, timestamp=date.today(), type="BUY")
    with pytest.raises(ValueError):
        Transaction(symbol="AAPL", quantity=1, price=0, timestamp=date.today(), type="BUY")
    with pytest.raises(ValueError):
        Transaction(symbol="AAPL", quantity=1, price=100, timestamp=date.today(), type="GIFT")


def test_portfolio_summary(sample_transactions: list[Transaction], sample_provider: MarketDataProvider) -> None:
    portfolio = Portfolio(sample_transactions)
    summary = portfolio.summary(sample_provider)

    assert summary.holdings["AAPL"].quantity == pytest.approx(7)
    assert summary.holdings["TSLA"].quantity == pytest.approx(0.5)
    assert summary.holdings["VTI"].quantity == pytest.approx(10)

    assert summary.total_invested == pytest.approx(3420)
    assert summary.market_value == pytest.approx(3599.3, rel=1e-4)
    assert summary.unrealized_gain == pytest.approx(179.3, rel=1e-4)

    assert summary.allocation["AAPL"] == pytest.approx(0.3796, abs=5e-4)
    assert summary.allocation["TSLA"] == pytest.approx(0.0347, abs=5e-4)
    assert summary.allocation["VTI"] == pytest.approx(0.5857, abs=5e-4)


def test_reporting_helpers(sample_transactions: list[Transaction], sample_provider: MarketDataProvider) -> None:
    portfolio = Portfolio(sample_transactions)
    text = generate_summary(portfolio, sample_provider)
    table = holdings_table(portfolio.holdings().values(), sample_provider)

    assert "Wealthfolio Summary" in text
    assert "AAPL" in text and "TSLA" in text and "VTI" in text
    assert "Symbol" in table and "Market Value" in table


def test_cli_integration(tmp_path, sample_transactions, sample_provider) -> None:
    transactions_path = tmp_path / "transactions.json"
    prices_path = tmp_path / "prices.json"

    transactions_payload = [
        {
            "symbol": txn.symbol,
            "quantity": txn.quantity,
            "price": txn.price,
            "date": txn.timestamp.isoformat(),
            "type": txn.type,
        }
        for txn in sample_transactions
    ]
    transactions_path.write_text(json.dumps(transactions_payload))
    prices_path.write_text(json.dumps(sample_provider.snapshot()))

    args = ["--transactions", str(transactions_path), "--prices", str(prices_path), "--table"]
    exit_code = cli_main(args)
    assert exit_code == 0
