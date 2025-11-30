import time
import requests
from .config import MARKETING_API_URL, SERVICE_USERNAME, SERVICE_PASSWORD, TOKEN_TTL

_token_cache = {"token": None, "expires_at": 0}

def get_service_token():
    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 5:
        return _token_cache["token"]

    resp = requests.post(f"{MARKETING_API_URL}/api/auth/login",
                         json={"Username": SERVICE_USERNAME, "Password": SERVICE_PASSWORD},
                         timeout=10)
    resp.raise_for_status()
    body = resp.json()
    token = body.get("Token") or body.get("token")
    if not token:
        raise RuntimeError("No token received from MarketingAPI login")
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + TOKEN_TTL
    return token