import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import json
import time
from unittest import mock

import pytest

# We'll import after writing modules

def test_get_tokens_refreshes_when_expired(monkeypatch):
    from importlib import reload
    import auth

    expired = {
        "access_token": "old",
        "refresh_token": "ref",
        "expires_in": 3600,
        "ts": time.time() - 4000,
    }

    def fake_run(cmd, capture_output=False, text=False, check=False):
        class Res:
            stdout = json.dumps(expired)
        return Res()

    monkeypatch.setattr(auth.subprocess, "run", fake_run)

    new_tokens = {
        "access_token": "new",
        "refresh_token": "ref2",
        "expires_in": 3600,
    }

    def fake_post(url, data):
        class Resp:
            def raise_for_status(self):
                pass
            def json(self):
                return new_tokens
        return Resp()

    monkeypatch.setattr(auth.requests, "post", fake_post)

    tokens = reload(auth).get_tokens()
    assert tokens["access_token"] == "new"
    assert tokens["refresh_token"] == "ref2"


def test_list_tickets_uses_bearer(monkeypatch):
    import saas_server

    def fake_get_tokens(aud=None):
        return {"access_token": "tok"}

    monkeypatch.setattr(saas_server, "get_tokens", fake_get_tokens)

    called = {}
    def fake_get(url, headers):
        called['headers'] = headers
        class Resp:
            def raise_for_status(self):
                pass
            def json(self):
                return {"tickets": [{"subject": "hello"}]}
        return Resp()

    monkeypatch.setattr(saas_server.requests, "get", fake_get)

    result = saas_server.list_tickets("dummy")
    assert called['headers']["Authorization"] == "Bearer tok"
    assert result[0]['subject'] == "hello"

def test_client_uses_bearer_header(monkeypatch):
    def fake_get_tokens(aud=None):
        return {"access_token": "abc"}
    monkeypatch.setattr("auth.get_tokens", fake_get_tokens)
    import importlib
    saas_client = importlib.import_module("saas_client")
    importlib.reload(saas_client)
    assert saas_client.transport.headers["Authorization"] == "Bearer abc"


