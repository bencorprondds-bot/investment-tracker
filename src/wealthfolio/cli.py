"""Command line interface for Wealthfolio."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List

from .portfolio import Portfolio, Transaction
from .providers import MarketDataProvider
from .report import generate_summary, holdings_table

DATE_FORMATS = ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Wealthfolio portfolio summaries")
    repo_root = Path(__file__).resolve().parents[2]
    parser.add_argument(
        "--transactions",
        type=Path,
        default=repo_root / "data" / "sample_transactions.json",
        help="Path to a JSON file containing a list of transactions",
    )
    parser.add_argument(
        "--prices",
        type=Path,
        default=repo_root / "data" / "sample_prices.json",
        help="Path to a JSON file containing a mapping of asset prices",
    )
    parser.add_argument(
        "--table",
        action="store_true",
        help="Display the holdings table in addition to the summary",
    )
    return parser.parse_args(argv)


def load_transactions(path: Path) -> List[Transaction]:
    payload = json.loads(path.read_text())
    transactions: List[Transaction] = []
    for entry in payload:
        timestamp = _parse_date(entry["date"])
        transactions.append(
            Transaction(
                symbol=entry["symbol"],
                quantity=float(entry["quantity"]),
                price=float(entry["price"]),
                timestamp=timestamp,
                type=entry.get("type", "BUY"),
            ),
        )
    return transactions


def load_prices(path: Path) -> MarketDataProvider:
    data = json.loads(path.read_text())
    provider = MarketDataProvider()
    provider.update(data)
    return provider


def _parse_date(raw: str) -> date:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    msg = f"Unsupported date format: {raw}"
    raise ValueError(msg)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    transactions = load_transactions(args.transactions)
    provider = load_prices(args.prices)

    portfolio = Portfolio(transactions)
    print(generate_summary(portfolio, provider))
    if args.table:
        print()
        print(holdings_table(portfolio.holdings().values(), provider))
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    raise SystemExit(main())
