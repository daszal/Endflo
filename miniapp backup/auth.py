"""
Telegram Mini App initData validation.

Telegram sends initData as a query string (`key=value&...` pairs) that includes
a `hash` parameter. The hash is an HMAC-SHA256 of the sorted key=value pairs
(excluding `hash` itself), signed with a secret derived from the bot token.

Validation steps:
  1. Parse the initData query string
  2. Check auth_date freshness (within 24h by default)
  3. Compute HMAC-SHA256(data_check_string, secret_key)
  4. Compare computed hash with the `hash` field
"""
import hashlib, hmac, json, os, time
from urllib.parse import parse_qs, unquote

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
MAX_AGE_SECONDS = 86400  # 24 hours


class AuthError(Exception):
    """Raised when initData validation fails."""


def _secret_key() -> bytes:
    """Derive the HMAC secret from the bot token."""
    return hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()


def _parse_init_data(data: str) -> dict[str, str]:
    """Parse a URL-encoded query string, preserving raw values."""
    result = {}
    for pair in data.split("&"):
        if "=" in pair:
            key, val = pair.split("=", 1)
            result[unquote(key)] = unquote(val)
    return result


def validate(init_data: str, max_age: int = MAX_AGE_SECONDS) -> dict:
    """
    Validate Telegram initData and return parsed fields.

    Args:
        init_data: The raw query string from telegram WebApp.initData
        max_age: Maximum age in seconds (default 24h)

    Returns:
        dict with at least: id, first_name, username (optional)

    Raises:
        AuthError: If validation fails for any reason
    """
    if not BOT_TOKEN:
        raise AuthError("TELEGRAM_BOT_TOKEN not configured")

    if not init_data:
        raise AuthError("Missing initData")

    params = _parse_init_data(init_data)

    # Check freshness
    auth_date = int(params.get("auth_date", "0"))
    if auth_date == 0:
        raise AuthError("Missing auth_date in initData")

    now = int(time.time())
    if now - auth_date > max_age:
        raise AuthError(
            f"initData expired (age: {now - auth_date}s, max: {max_age}s)"
        )

    # Verify hash
    received_hash = params.pop("hash", None)
    if not received_hash:
        raise AuthError("Missing hash in initData")

    # Build data-check-string: sorted keys, excluding 'hash'
    data_check_parts = []
    for key in sorted(params.keys()):
        data_check_parts.append(f"{key}={params[key]}")
    data_check_string = "\n".join(data_check_parts)

    computed_hash = hmac.new(
        _secret_key(), data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise AuthError("Hash mismatch — initData may be forged")

    # Parse user data
    user_str = params.get("user", "{}")
    try:
        user = json.loads(user_str)
    except json.JSONDecodeError:
        raise AuthError("Invalid user JSON in initData")

    return {
        "id": user.get("id"),
        "first_name": user.get("first_name", ""),
        "username": user.get("username", ""),
    }
