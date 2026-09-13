"""
Central configuration, loaded from environment variables.

All values are read at call time (not import time) so tests can monkeypatch
os.environ freely.
"""

import os


class ConfigError(Exception):
    """Raised when required configuration is missing for a chosen platform."""


class Config:
    # --- X / Twitter ---
    @property
    def x_bearer_token(self) -> str:
        return os.environ.get("X_BEARER_TOKEN", "")

    @property
    def x_user_id(self) -> str:
        return os.environ.get("X_USER_ID", "")

    @property
    def x_username(self) -> str:
        return os.environ.get("X_USERNAME", "")

    # --- Instagram (official Graph API, Business/Creator accounts only) ---
    @property
    def ig_access_token(self) -> str:
        return os.environ.get("IG_ACCESS_TOKEN", "")

    @property
    def ig_business_account_id(self) -> str:
        return os.environ.get("IG_BUSINESS_ACCOUNT_ID", "")

    # --- Google Sheets ---
    @property
    def google_service_account_file(self) -> str:
        return os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")

    @property
    def google_sheet_id(self) -> str:
        return os.environ.get("GOOGLE_SHEET_ID", "")

    @property
    def google_sheet_tab_x(self) -> str:
        return os.environ.get("GOOGLE_SHEET_TAB_X", "X Unfollowers")

    @property
    def google_sheet_tab_instagram(self) -> str:
        return os.environ.get("GOOGLE_SHEET_TAB_INSTAGRAM", "Instagram Follower Counts")

    # --- Local snapshot storage ---
    @property
    def snapshot_dir(self) -> str:
        return os.environ.get("SNAPSHOT_DIR", ".")

    def require_x(self) -> None:
        if not self.x_bearer_token:
            raise ConfigError("Missing X_BEARER_TOKEN environment variable.")
        if not self.x_user_id and not self.x_username:
            raise ConfigError("Set X_USER_ID or X_USERNAME to identify your X account.")

    def require_instagram(self) -> None:
        if not self.ig_access_token:
            raise ConfigError("Missing IG_ACCESS_TOKEN environment variable.")
        if not self.ig_business_account_id:
            raise ConfigError("Missing IG_BUSINESS_ACCOUNT_ID environment variable.")


config = Config()
