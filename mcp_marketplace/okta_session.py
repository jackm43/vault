"""Utility for retrieving and caching Okta OAuth tokens."""

from __future__ import annotations

import os
import time
from typing import Optional
import requests


class OktaSession:
    """Simple helper for managing an Okta OAuth access token."""

    def __init__(self, issuer_url: str, client_id: str, refresh_token: str) -> None:
        self.issuer_url = issuer_url.rstrip("/")
        self.client_id = client_id
        self.refresh_token = refresh_token
        self._access_token: Optional[str] = None
        self._expires_at: float = 0

    def token(self) -> str:
        """Return a valid access token, refreshing if needed."""
        if not self._access_token or time.time() >= self._expires_at:
            self._refresh()
        assert self._access_token
        return self._access_token

    def _refresh(self) -> None:
        token_url = f"{self.issuer_url}/v1/token"
        resp = requests.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": self.refresh_token,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        self._expires_at = time.time() + data.get("expires_in", 3600) - 60


def from_env() -> Optional[OktaSession]:
    issuer = os.getenv("OKTA_ISSUER")
    client_id = os.getenv("OKTA_CLIENT_ID")
    refresh_token = os.getenv("OKTA_REFRESH_TOKEN")
    if issuer and client_id and refresh_token:
        return OktaSession(issuer, client_id, refresh_token)
    return None
