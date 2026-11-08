# DEV-01 offline contracts

Created 2026-11-08 15:22 KST — CD2 / developer.

Run the deterministic, credential-free example from the repository root. The mode must be selected explicitly:

```powershell
python -m trading.main --mode offline
python -m unittest discover -s tests -p 'test_trading_dev01.py' -v
```

The package exposes `Settings`, `Broker`, `FakeBroker`, and immutable value objects in `models.py`. Identifiers are strings (so leading zeroes survive), monetary values use `Decimal`, and quantities are positive integers. `BrokerError.code` is stable for machine handling; current codes include `SYMBOL_UNKNOWN`, `INVALID_IDENTIFIER`, `INVALID_ORDER`, and `DUPLICATE_CLIENT_ORDER_ID`.

`offline` only accepts `broker=fake`; no credentials or network are used. Omitting `--mode` or `TRADER_MODE` is an error and never selects a mode implicitly. `paper` requires `broker=kis-paper` plus `TRADER_ACCOUNT_ID`, `TRADER_APP_KEY`, and `TRADER_APP_SECRET`. Paper transport is deliberately not implemented yet, so the CLI exits with a clear configuration failure when credentials are absent and `run()` raises an explicit unsupported-transport error if valid settings are supplied. `live` is rejected. No mode silently changes to another mode.

DEV-02 can implement the `Broker` protocol using these `Quote`, `OrderRequest`, and `OrderResult` types while preserving the safe error codes. This increment does not implement KIS transport, persistent order state, risk controls, or NAS deployment.
