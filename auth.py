"""Token helper using 1Password for caching and refresh tokens via Okta."""
import json
import os
import subprocess
import time
from typing import Optional, Dict

import requests


OP_ITEM_PREFIX = os.getenv("OP_TOKEN_PREFIX", "mcp")
OKTA_ISSUER = os.getenv("OKTA_ISSUER", "https://example.okta.com/oauth2/default")
OKTA_CLIENT_ID = os.getenv("OKTA_CLIENT_ID", "client")
TOKEN_ENDPOINT = f"{OKTA_ISSUER}/v1/token"


def _op_item_name(audience: Optional[str]) -> str:
    return f"{OP_ITEM_PREFIX}-{audience or 'default'}"


def _read_tokens(item: str) -> Optional[Dict]:
    try:
        result = subprocess.run([
            "op",
            "read",
            f"op://private/{item}/tokens"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except Exception:
        data = os.getenv(f"TOKENS_{item.upper()}")
        if data:
            return json.loads(data)
    return None


def _write_tokens(item: str, tokens: Dict) -> None:
    payload = json.dumps(tokens)
    try:
        subprocess.run([
            "op",
            "item",
            "edit",
            item,
            f"tokens={payload}"],
            check=True,
        )
    except Exception:
        os.environ[f"TOKENS_{item.upper()}"] = payload


def _refresh(refresh_token: str, audience: Optional[str]) -> Dict:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": OKTA_CLIENT_ID,
    }
    if audience:
        data["audience"] = audience
    r = requests.post(TOKEN_ENDPOINT, data=data)
    r.raise_for_status()
    new_tokens = r.json()
    new_tokens["ts"] = int(time.time())
    return new_tokens


def get_tokens(audience: Optional[str] = None) -> Dict:
    """Return tokens cached in 1Password, refreshing if expired."""
    item = _op_item_name(audience)
    tokens = _read_tokens(item)
    if not tokens:
        raise RuntimeError("Token cache missing")

    expires_at = tokens.get("ts", 0) + tokens.get("expires_in", 0) - 60
    if expires_at <= time.time():
        tokens = _refresh(tokens["refresh_token"], audience)
        _write_tokens(item, tokens)
    return tokens

