from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import requests
import jwt

from mcp.server.fastmcp import FastMCP
from auth import get_tokens

mcp = FastMCP("SaaS-Bridge")

OKTA_ISSUER = os.getenv("OKTA_ISSUER", "https://example.okta.com/oauth2/default")
OKTA_JWKS_URL = f"{OKTA_ISSUER}/v1/keys"

_jwks_cache = None


security = HTTPBearer()

def verify_okta_token(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        global _jwks_cache
        if _jwks_cache is None:
            resp = requests.get(OKTA_JWKS_URL)
            resp.raise_for_status()
            _jwks_cache = resp.json()
        header = jwt.get_unverified_header(token)
        key = next(k for k in _jwks_cache["keys"] if k["kid"] == header["kid"])
        jwt.decode(token, jwt.algorithms.RSAAlgorithm.from_jwk(key),
                   algorithms=["RS256"], audience=None, issuer=OKTA_ISSUER)
    except Exception as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    return token

ZENDESK_DOMAIN = os.getenv("ZENDESK_DOMAIN", "yourcompany.zendesk.com")


@mcp.tool()
def list_tickets(token: str = Depends(verify_okta_token)):
    tk = get_tokens("zendesk")["access_token"]
    r = requests.get(f"https://{ZENDESK_DOMAIN}/api/v2/tickets.json",
                     headers={"Authorization": f"Bearer {tk}"})
    r.raise_for_status()
    return r.json()["tickets"]


@mcp.tool()
def create_ticket(subject: str, body: str, token: str = Depends(verify_okta_token)):
    tk = get_tokens("zendesk")["access_token"]
    payload = {"ticket": {"subject": subject, "comment": {"body": body}}}
    r = requests.post(f"https://{ZENDESK_DOMAIN}/api/v2/tickets.json",
                      headers={"Authorization": f"Bearer {tk}",
                               "Content-Type": "application/json"},
                      json=payload)
    r.raise_for_status()
    return r.json()

SF_DOMAIN = os.getenv("SF_DOMAIN", "yourinstance.my.salesforce.com")


@mcp.tool()
def list_accounts(token: str = Depends(verify_okta_token)):
    tk = get_tokens("salesforce")["access_token"]
    soql = "SELECT Name FROM Account LIMIT 5"
    r = requests.get(f"https://{SF_DOMAIN}/services/data/v58.0/query/",
                     headers={"Authorization": f"Bearer {tk}"}, params={"q": soql})
    r.raise_for_status()
    return r.json()["records"]


@mcp.tool()
def create_lead(last_name: str, company: str, token: str = Depends(verify_okta_token)):
    tk = get_tokens("salesforce")["access_token"]
    payload = {"LastName": last_name, "Company": company}
    r = requests.post(f"https://{SF_DOMAIN}/services/data/v58.0/sobjects/Lead/",
                      headers={"Authorization": f"Bearer {tk}",
                               "Content-Type": "application/json"},
                      json=payload)
    r.raise_for_status()
    return r.json()

OKTA_DOMAIN = os.getenv("OKTA_DOMAIN", "your_okta_domain")


@mcp.tool()
def list_users(token: str = Depends(verify_okta_token)):
    tk = get_tokens("okta")["access_token"]
    r = requests.get(f"https://{OKTA_DOMAIN}/api/v1/users",
                     headers={"Authorization": f"SSWS {tk}"})
    r.raise_for_status()
    return r.json()


@mcp.tool()
def create_user(email: str, first: str, last: str, token: str = Depends(verify_okta_token)):
    tk = get_tokens("okta")["access_token"]
    payload = {
        "profile": {"firstName": first, "lastName": last,
                    "email": email, "login": email},
        "credentials": {"password": {"value": "TempP@ssword123"}}
    }
    r = requests.post(f"https://{OKTA_DOMAIN}/api/v1/users?activate=true",
                      headers={"Authorization": f"SSWS {tk}",
                               "Content-Type": "application/json"},
                      json=payload)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    mcp.serve()

