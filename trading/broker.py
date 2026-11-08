# Created 2026-11-08 15:20 KST: DEV-01 broker protocol and deterministic fake, CD2 / developer.
"""Broker contract and deterministic in-memory offline implementation."""

from datetime import datetime, timezone
from decimal import Decimal
from decimal import Decimal
from typing import Protocol

from .models import OrderRequest, OrderResult, OrderStatus, Quote, Side


class BrokerError(Exception):
    """Stable broker failure carrying a safe machine code and message."""

    def __init__(self, code: str, message: str):
        self.code, self.message = code, message
        super().__init__(f"{code}: {message}")


class Broker(Protocol):
    def get_quote(self, symbol: str) -> Quote: ...
    def submit_order(self, request: OrderRequest) -> OrderResult: ...


class FakeBroker:
    """Repeatable quotes and IDs; no network, credentials, or real orders."""

    def __init__(self, quotes=None):
        self.quotes = quotes or {"005930": Decimal("70000.00")}
        self.orders: dict[str, OrderResult] = {}

    def get_quote(self, symbol: str) -> Quote:
        if symbol not in self.quotes:
            raise BrokerError("SYMBOL_UNKNOWN", "symbol is not present in fake quote fixture")
        return Quote(symbol, self.quotes[symbol], "KRW", datetime(2026, 1, 2, tzinfo=timezone.utc))

    def submit_order(self, request: OrderRequest) -> OrderResult:
        if not request.client_order_id or not request.account_id or not request.symbol:
            raise BrokerError("INVALID_IDENTIFIER", "client order, account, and symbol identifiers are required")
        if not isinstance(request.side, Side):
            raise BrokerError("INVALID_ORDER", "side must be a supported Side value")
        if type(request.quantity) is not int or request.quantity <= 0:
            raise BrokerError("INVALID_ORDER", "quantity must be a positive integer")
        if (not isinstance(request.limit_price, Decimal) or not request.limit_price.is_finite()
                or request.limit_price <= 0):
            raise BrokerError("INVALID_ORDER", "limit_price must be a finite positive Decimal")
        if request.client_order_id in self.orders:
            raise BrokerError("DUPLICATE_CLIENT_ORDER_ID", "client order identifier already exists")
        result = OrderResult(request.client_order_id, f"FAKE-{request.client_order_id}", OrderStatus.ACCEPTED, request.quantity)
        self.orders[request.client_order_id] = result
        return result

