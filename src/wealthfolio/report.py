"""Utilities for rendering textual portfolio reports."""

from __future__ import annotations

from typing import Iterable

from .portfolio import Holding, Portfolio
from .providers import MarketDataProvider


def generate_summary(portfolio: Portfolio, provider: MarketDataProvider) -> str:
    """Return a friendly textual summary for a portfolio."""

    summary = portfolio.summary(provider)
    lines = [
        "Wealthfolio Summary",
        "===================",
        f"Total invested: ${summary.total_invested:,.2f}",
        f"Market value:   ${summary.market_value:,.2f}",
        f"Unrealized P/L: ${summary.unrealized_gain:,.2f}",
        "",
        "Holdings:",
    ]

    if not summary.holdings:
        lines.append("  (no positions)")
    else:
        for symbol, holding in sorted(summary.holdings.items()):
            allocation = summary.allocation.get(symbol, 0.0)
            market_value = holding.market_value(provider)
            lines.append(
                f"  - {symbol}: {holding.quantity:,.4f} shares at ${holding.cost_basis:,.2f} cost basis",
            )
            lines.append(
                f"       Market value: ${market_value:,.2f} | Allocation: {allocation:.1%}",
            )

    return "\n".join(lines)


def holdings_table(holdings: Iterable[Holding], provider: MarketDataProvider) -> str:
    """Render a compact table containing key metrics for holdings."""

    header = f"{'Symbol':<10}{'Quantity':>12}{'Cost Basis':>16}{'Market Value':>18}"
    separator = "-" * len(header)
    rows = [header, separator]
    for holding in holdings:
        market_value = holding.market_value(provider)
        rows.append(
            "{symbol:<10}{quantity:>12,.4f}${cost:>15,.2f}${value:>17,.2f}".format(
                symbol=holding.symbol,
                quantity=holding.quantity,
                cost=holding.cost_basis,
                value=market_value,
            ),
        )
    return "\n".join(rows)
