# Created 2026-11-08 15:20 KST: DEV-01 mode and credential checks, CD2 / developer.
"""Fail-closed execution settings loaded from explicit values or environment."""

from dataclasses import dataclass
import os


class ConfigError(ValueError):
    """Invalid or incomplete execution configuration."""


@dataclass(frozen=True)
class Settings:
    mode: str
    broker: str
    account_id: str | None = None
    app_key: str | None = None
    app_secret: str | None = None

    def validate(self) -> "Settings":
        if self.mode not in {"offline", "paper"}:
            raise ConfigError("unsupported mode; allowed modes: offline, paper")
        if self.mode == "offline":
            if self.broker != "fake":
                raise ConfigError("offline mode requires broker=fake")
            return self
        if self.broker != "kis-paper":
            raise ConfigError("paper mode requires broker=kis-paper")
        missing = [key for key, value in (("TRADER_ACCOUNT_ID", self.account_id),
                   ("TRADER_APP_KEY", self.app_key), ("TRADER_APP_SECRET", self.app_secret)) if not value]
        if missing:
            raise ConfigError("paper mode missing required credentials: " + ", ".join(missing))
        return self

    @classmethod
    def from_env(cls, environ=None) -> "Settings":
        env = os.environ if environ is None else environ
        mode = env.get("TRADER_MODE")
        if not mode:
            raise ConfigError("execution mode must be explicit: set TRADER_MODE to offline or paper")
        return cls(mode=mode.lower(),
                   broker=env.get("TRADER_BROKER", "").lower(),
                   account_id=env.get("TRADER_ACCOUNT_ID"), app_key=env.get("TRADER_APP_KEY"),
                   app_secret=env.get("TRADER_APP_SECRET")).validate()

