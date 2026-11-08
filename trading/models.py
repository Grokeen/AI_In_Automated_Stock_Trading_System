# Created 2026-11-08 15:20 KST: DEV-01 common models, CD2 / developer.
"""Shared value objects. Identifiers stay strings and money uses Decimal."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: Decimal
    currency: str
    observed_at: datetime


@dataclass(frozen=True)
class OrderRequest:
    client_order_id: str
    account_id: str
    symbol: str
    side: Side
    quantity: int
    limit_price: Decimal


@dataclass(frozen=True)
class OrderResult:
    client_order_id: str
    broker_order_id: str
    status: OrderStatus
    accepted_quantity: int
    error_code: str | None = None
    error_message: str | None = None

