# Created 2026-11-08 15:22 KST: DEV-01 offline contract tests, CD2 / developer.
"""Regression coverage for DEV-01 only; legacy NAS tests remain untouched."""

import unittest
from decimal import Decimal

from trading.broker import BrokerError, FakeBroker
from trading.config import ConfigError, Settings
from trading.main import main, run
from trading.models import OrderRequest, Side


class Dev01Tests(unittest.TestCase):
    def test_mode_must_be_explicit_and_offline_needs_no_credentials(self):
        with self.assertRaisesRegex(ConfigError, "mode must be explicit"):
            Settings.from_env({})
        with self.assertRaises(SystemExit) as missing_cli_mode:
            main([])
        self.assertEqual(missing_cli_mode.exception.code, 2)
        settings = Settings.from_env({"TRADER_MODE": "offline", "TRADER_BROKER": "fake"})
        self.assertEqual(settings.mode, "offline")
        self.assertEqual(run(settings), run(settings))

    def test_valid_paper_settings_fail_as_unsupported_transport(self):
        settings = Settings("paper", "kis-paper", "00012345", "fake-key", "fake-secret").validate()
        with self.assertRaisesRegex(RuntimeError, "paper transport is not implemented"):
            run(settings)

    def test_paper_missing_credentials_and_broker_mismatch_fail_closed(self):
        with self.assertRaisesRegex(ConfigError, "missing required credentials"):
            Settings("paper", "kis-paper").validate()
        with self.assertRaisesRegex(ConfigError, "requires broker=kis-paper"):
            Settings("paper", "fake", "a", "k", "s").validate()

    def test_live_is_not_accepted(self):
        with self.assertRaisesRegex(ConfigError, "unsupported mode"):
            Settings("live", "kis-live", "a", "k", "s").validate()

    def test_decimal_quantity_and_leading_zero_identifiers_preserved(self):
        broker = FakeBroker()
        result = broker.submit_order(OrderRequest("order-001", "00012345", "005930",
                                                  Side.BUY, 3, Decimal("70000.10")))
        self.assertEqual(result.broker_order_id, "FAKE-order-001")
        self.assertEqual(result.accepted_quantity, 3)
        self.assertEqual(broker.get_quote("005930").price, Decimal("70000.00"))

    def test_unknown_symbol_and_duplicate_order_have_stable_codes(self):
        broker = FakeBroker()
        with self.assertRaises(BrokerError) as missing:
            broker.get_quote("999999")
        self.assertEqual(missing.exception.code, "SYMBOL_UNKNOWN")
        req = OrderRequest("same", "0001", "005930", Side.BUY, 1, Decimal("1"))
        broker.submit_order(req)
        with self.assertRaises(BrokerError) as duplicate:
            broker.submit_order(req)
        self.assertEqual(duplicate.exception.code, "DUPLICATE_CLIENT_ORDER_ID")

    def test_invalid_order_boundaries_rejected_with_stable_error(self):
        invalid = (
            OrderRequest("x", "a", "005930", Side.BUY, 0, Decimal("1")),
            OrderRequest("x", "a", "005930", "hold", 1, Decimal("1")),
            OrderRequest("x", "a", "005930", Side.BUY, True, Decimal("1")),
            OrderRequest("x", "a", "005930", Side.BUY, 1, 1.0),
            OrderRequest("x", "a", "005930", Side.BUY, 1, Decimal("NaN")),
            OrderRequest("x", "a", "005930", Side.BUY, 1, Decimal("Infinity")),
            OrderRequest("x", "a", "005930", Side.BUY, 1, Decimal("0")),
            OrderRequest("x", "a", "005930", Side.BUY, 1, Decimal("-0.01")),
        )
        for request in invalid:
            with self.subTest(request=request):
                with self.assertRaises(BrokerError) as rejected:
                    FakeBroker().submit_order(request)
                self.assertEqual(rejected.exception.code, "INVALID_ORDER")


if __name__ == "__main__":
    unittest.main()
