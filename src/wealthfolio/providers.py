"""Data provider utilities for fetching market prices."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, Mapping


@dataclass(frozen=True)
class PricePoint:
    """Represents the price of an asset on a specific date."""

    symbol: str
    price: float
    as_of: date

    def __post_init__(self) -> None:
        if self.price <= 0:
            msg = "Price must be a positive value"
            raise ValueError(msg)


class MarketDataProvider:
    """Simple in-memory provider for market data."""

    def __init__(self, prices: Mapping[str, float] | None = None) -> None:
        self._prices: Dict[str, float] = dict(prices or {})

    def update(self, price_points: Iterable[PricePoint] | Mapping[str, float]) -> None:
        """Update the price store with the latest quotes."""

        if isinstance(price_points, Mapping):
            for symbol, price in price_points.items():
                self._validate_price(symbol, price)
                self._prices[symbol.upper()] = float(price)
            return

        for point in price_points:
            self._validate_price(point.symbol, point.price)
            self._prices[point.symbol.upper()] = float(point.price)

    def price_for(self, symbol: str) -> float:
        """Return the latest price for an asset."""

        key = symbol.upper()
        if key not in self._prices:
            msg = f"No price available for {symbol!r}"
            raise KeyError(msg)
        return self._prices[key]

    def _validate_price(self, symbol: str, price: float) -> None:
        if price <= 0:
            msg = f"Price for {symbol!r} must be positive"
            raise ValueError(msg)

    def snapshot(self) -> Dict[str, float]:
        """Return a copy of the tracked prices."""

        return dict(self._prices)
