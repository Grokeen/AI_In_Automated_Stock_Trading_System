# Created 2026-11-08 15:20 KST: DEV-01 minimal offline executable, CD2 / developer.
"""Run the deterministic offline demonstration: python -m trading.main --mode offline."""

import argparse
from dataclasses import asdict
from decimal import Decimal
import json
import os
import sys

from .broker import FakeBroker
from .config import Settings
from .models import OrderRequest, Side


def run(settings: Settings) -> dict:
    settings.validate()
    if settings.mode != "offline":
        raise RuntimeError("paper transport is not implemented in DEV-01")
    broker = FakeBroker()
    quote = broker.get_quote("005930")
    order = broker.submit_order(OrderRequest("demo-001", "paper-demo", quote.symbol,
                                               Side.BUY, 1, Decimal("70000.00")))
    return {"mode": settings.mode, "quote": {**asdict(quote), "price": str(quote.price), "observed_at": quote.observed_at.isoformat()},
            "order": {**asdict(order), "status": order.status.value}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="DEV-01 offline demo")
    parser.add_argument("--mode", choices=("offline", "paper"), required=True)
    args = parser.parse_args(argv)
    try:
        settings = Settings.from_env({"TRADER_MODE": args.mode,
                                      "TRADER_BROKER": "fake" if args.mode == "offline" else "kis-paper",
                                      "TRADER_ACCOUNT_ID": os.environ.get("TRADER_ACCOUNT_ID"),
                                      "TRADER_APP_KEY": os.environ.get("TRADER_APP_KEY"),
                                      "TRADER_APP_SECRET": os.environ.get("TRADER_APP_SECRET")})
        print(json.dumps(run(settings), ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, RuntimeError) as exc:
        print(f"trading: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
