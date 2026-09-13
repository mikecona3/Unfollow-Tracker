"""
Instagram follower tracking.

IMPORTANT LIMITATION: Meta's official Graph API (the only sanctioned way to
access Instagram programmatically) does not expose a list of individual
follower usernames -- only aggregate account metrics, including a total
follower count. So unlike the X provider, this cannot tell you *who*
unfollowed you, only *how many* followers you gained or lost between runs.

Getting actual follower usernames from Instagram would require unofficial
private-API libraries or browser automation against the Instagram web/app
UI, both of which violate Instagram's Terms of Service. This provider
intentionally does not do that.

Requires a Business or Creator Instagram account connected to a Facebook
Page, and a Graph API access token with the instagram_basic permission.
"""

from datetime import datetime, timezone

import requests

from ..config import config
from ..snapshot import load_snapshot, save_snapshot

PLATFORM = "instagram"
GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


def _fetch_follower_count() -> int:
    url = f"{GRAPH_API_BASE}/{config.ig_business_account_id}"
    params = {
        "fields": "followers_count",
        "access_token": config.ig_access_token,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "followers_count" not in data:
        raise RuntimeError(f"Unexpected Instagram Graph API response: {data}")
    return int(data["followers_count"])


def run() -> dict:
    """
    Fetch current follower count, diff against the previous snapshot, and
    return a result dict:
        {
            "platform": "instagram",
            "first_run": bool,
            "follower_count": int,
            "delta": int,              # negative means net follower loss
            "sheet_rows": [ [timestamp, count, delta], ... ],
        }

    Note: no usernames are ever returned here -- see module docstring.
    """
    config.require_instagram()

    current_count = _fetch_follower_count()
    previous = load_snapshot(config.snapshot_dir, PLATFORM)
    first_run = previous is None
    previous_count = previous.get("count") if previous else None

    delta = 0 if first_run else current_count - previous_count

    timestamp = datetime.now(timezone.utc).isoformat()
    sheet_rows = [] if first_run else [[timestamp, current_count, delta]]

    save_snapshot(
        config.snapshot_dir,
        PLATFORM,
        {"count": current_count, "checked_at": timestamp},
    )

    return {
        "platform": PLATFORM,
        "first_run": first_run,
        "follower_count": current_count,
        "delta": delta,
        "sheet_rows": sheet_rows,
    }
