"""
X (Twitter) unfollower detection.

Uses the X API v2 (requires at least Basic-tier paid API access — the free
tier does not expose the followers endpoint at usable volume) to fetch your
current follower list, then diffs it against the last saved snapshot to
find who unfollowed you since the previous run.
"""

from datetime import datetime, timezone

import tweepy

from ..config import config
from ..snapshot import load_snapshot, save_snapshot

PLATFORM = "x"


def _get_client() -> tweepy.Client:
    return tweepy.Client(bearer_token=config.x_bearer_token, wait_on_rate_limit=True)


def _resolve_user_id(client: tweepy.Client) -> str:
    if config.x_user_id:
        return config.x_user_id
    resp = client.get_user(username=config.x_username)
    if resp.data is None:
        raise RuntimeError(f"Could not resolve X username @{config.x_username} to a user ID.")
    return str(resp.data.id)


def _fetch_followers(client: tweepy.Client, user_id: str) -> dict:
    """Return {user_id: username} for all current followers."""
    followers = {}
    for response in tweepy.Paginator(
        client.get_users_followers,
        id=user_id,
        max_results=1000,
        user_fields=["username"],
    ):
        if response.data:
            for user in response.data:
                followers[str(user.id)] = user.username
    return followers


def run() -> dict:
    """
    Fetch current followers, diff against the previous snapshot, and return
    a result dict:
        {
            "platform": "x",
            "first_run": bool,
            "follower_count": int,
            "unfollowers": [ {"user_id": ..., "username": ...}, ... ],
            "sheet_rows": [ [timestamp, user_id, username], ... ],
        }
    """
    config.require_x()
    client = _get_client()
    user_id = _resolve_user_id(client)

    current_followers = _fetch_followers(client, user_id)
    previous_followers = load_snapshot(config.snapshot_dir, PLATFORM) or {}

    first_run = not previous_followers
    unfollower_ids = [] if first_run else [
        uid for uid in previous_followers if uid not in current_followers
    ]

    timestamp = datetime.now(timezone.utc).isoformat()
    unfollowers = [
        {"user_id": uid, "username": previous_followers.get(uid, "unknown")}
        for uid in unfollower_ids
    ]
    sheet_rows = [[timestamp, u["user_id"], u["username"]] for u in unfollowers]

    save_snapshot(config.snapshot_dir, PLATFORM, current_followers)

    return {
        "platform": PLATFORM,
        "first_run": first_run,
        "follower_count": len(current_followers),
        "unfollowers": unfollowers,
        "sheet_rows": sheet_rows,
    }
