"""Core portfolio modelling and analytics."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Mapping

from .providers import MarketDataProvider


@dataclass(frozen=True)
class Transaction:
    """Represents a buy or sell action for a security."""

    symbol: str
    quantity: float
    price: float
    timestamp: date
    type: str  # "BUY" or "SELL"

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            msg = "Quantity must be positive"
            raise ValueError(msg)
        if self.price <= 0:
            msg = "Price must be positive"
            raise ValueError(msg)
        if self.type.upper() not in {"BUY", "SELL"}:
            msg = "Transaction type must be BUY or SELL"
            raise ValueError(msg)

    @property
    def cash_flow(self) -> float:
        """Return the cash flow impact of the transaction."""

        sign = 1 if self.type.upper() == "BUY" else -1
        return sign * self.quantity * self.price

    @property
    def signed_quantity(self) -> float:
        """Signed quantity where sells reduce the position."""

        return self.quantity if self.type.upper() == "BUY" else -self.quantity


@dataclass(frozen=True)
class Holding:
    """Current position for a security."""

    symbol: str
    quantity: float
    cost_basis: float

    def market_value(self, provider: MarketDataProvider) -> float:
        return self.quantity * provider.price_for(self.symbol)


@dataclass(frozen=True)
class PortfolioSummary:
    """Snapshot summary for reporting."""

    holdings: Mapping[str, Holding]
    total_invested: float
    market_value: float
    allocation: Mapping[str, float]

    @property
    def unrealized_gain(self) -> float:
        return self.market_value - self.total_invested


class Portfolio:
    """A collection of transactions with valuation helpers."""

    def __init__(self, transactions: Iterable[Transaction] | None = None) -> None:
        self._transactions: List[Transaction] = list(transactions or [])

    def add(self, transaction: Transaction) -> None:
        self._transactions.append(transaction)

    def extend(self, transactions: Iterable[Transaction]) -> None:
        self._transactions.extend(transactions)

    @property
    def transactions(self) -> List[Transaction]:
        return list(self._transactions)

    def holdings(self) -> Dict[str, Holding]:
        positions: Dict[str, Dict[str, float]] = defaultdict(lambda: {"qty": 0.0, "cost": 0.0})
        for txn in self._transactions:
            symbol = txn.symbol.upper()
            position = positions[symbol]

            if txn.type.upper() == "BUY":
                position["qty"] += txn.quantity
                position["cost"] += txn.quantity * txn.price
                continue

            # Handle sell transactions by reducing cost basis proportionally.
            if position["qty"] <= 0:
                msg = f"Cannot sell shares for {symbol} without an existing position"
                raise ValueError(msg)

            if txn.quantity > position["qty"] + 1e-9:
                msg = f"Cannot sell more shares than currently held for {symbol}"
                raise ValueError(msg)

            average_cost = position["cost"] / position["qty"] if position["qty"] else 0.0
            reduction = average_cost * txn.quantity
            position["qty"] -= txn.quantity
            position["cost"] -= reduction

            # Guard against floating point drift leaving tiny negative remnants.
            if position["qty"] < 1e-9:
                position["qty"] = 0.0
                position["cost"] = 0.0
            else:
                position["cost"] = max(position["cost"], 0.0)

        holdings: Dict[str, Holding] = {}
        for symbol, values in positions.items():
            qty = round(values["qty"], 4)
            cost = round(values["cost"], 2)
            if qty <= 0:
                continue
            holdings[symbol] = Holding(symbol=symbol, quantity=qty, cost_basis=cost)
        return holdings

    def total_invested(self) -> float:
        return sum(txn.cash_flow for txn in self._transactions if txn.type.upper() == "BUY")

    def summary(self, provider: MarketDataProvider) -> PortfolioSummary:
        holdings = self.holdings()
        market_values: Dict[str, float] = {
            symbol: holding.market_value(provider) for symbol, holding in holdings.items()
        }
        market_value = sum(market_values.values())
        total_invested = sum(holding.cost_basis for holding in holdings.values())
        allocation = {
            symbol: 0.0 if market_value == 0 else value / market_value
            for symbol, value in market_values.items()
        }
        return PortfolioSummary(
            holdings=holdings,
            total_invested=total_invested,
            market_value=market_value,
            allocation=allocation,
        )
