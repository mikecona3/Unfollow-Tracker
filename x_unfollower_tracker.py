#!/usr/bin/env python3
"""
X (Twitter) Unfollower Tracker
================================
Tracks who unfollows you on X by snapshotting your follower list on each run,
diffing it against the previous snapshot, and exporting the "who unfollowed
you" list to a Google Sheet.

SETUP
-----
1. X / Twitter API (v2) access:
   - Needs at least "Basic" tier API access (the free tier does not expose
     the followers endpoint at usable volume).
   - Create a project/app at https://developer.x.com and grab a Bearer Token.
   - Set it as an env var:  export X_BEARER_TOKEN="..."
   - Set your numeric user ID (or handle) below or via env var X_USER_ID /
     X_USERNAME.

2. Google Sheets export:
   - Create a Google Cloud service account, enable the Sheets + Drive APIs,
     download the JSON key file.
   - Share your target Google Sheet with the service account's email
     (found in the JSON key as "client_email"), giving it Editor access.
   - Set the path to the key file via env var GOOGLE_SERVICE_ACCOUNT_FILE,
     and the target spreadsheet ID via GOOGLE_SHEET_ID (the long ID in the
     sheet's URL).

3. Install dependencies:
   pip install tweepy gspread google-auth --break-system-packages

USAGE
-----
   python x_unfollower_tracker.py

Run this periodically (e.g. via cron or a scheduled task). Each run:
   - Fetches your current follower list from X.
   - Compares it to the last saved snapshot (followers_snapshot.json).
   - Prints and appends any newly-detected unfollowers to the Google Sheet.
   - Saves the current follower list as the new snapshot for next time.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import tweepy

# ---------------------------------------------------------------------------
# Configuration (env vars preferred; fill in defaults here if you'd rather
# hardcode them for local/personal use)
# ---------------------------------------------------------------------------
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN", "")
X_USER_ID = os.environ.get("X_USER_ID", "")          # numeric ID, preferred
X_USERNAME = os.environ.get("X_USERNAME", "")        # fallback: @handle, no "@"

GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get(
    "GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"
)
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")
GOOGLE_SHEET_TAB = os.environ.get("GOOGLE_SHEET_TAB", "Unfollowers")

SNAPSHOT_FILE = Path("followers_snapshot.json")


# ---------------------------------------------------------------------------
# X API helpers
# ---------------------------------------------------------------------------
def get_client() -> tweepy.Client:
    if not X_BEARER_TOKEN:
        sys.exit("Missing X_BEARER_TOKEN environment variable.")
    return tweepy.Client(bearer_token=X_BEARER_TOKEN, wait_on_rate_limit=True)


def resolve_user_id(client: tweepy.Client) -> str:
    if X_USER_ID:
        return X_USER_ID
    if not X_USERNAME:
        sys.exit("Set X_USER_ID or X_USERNAME to identify your account.")
    resp = client.get_user(username=X_USERNAME)
    if resp.data is None:
        sys.exit(f"Could not resolve username @{X_USERNAME} to a user ID.")
    return str(resp.data.id)


def fetch_followers(client: tweepy.Client, user_id: str) -> dict:
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


# ---------------------------------------------------------------------------
# Snapshot diffing
# ---------------------------------------------------------------------------
def load_previous_snapshot() -> dict:
    if SNAPSHOT_FILE.exists():
        return json.loads(SNAPSHOT_FILE.read_text())
    return {}


def save_snapshot(followers: dict) -> None:
    SNAPSHOT_FILE.write_text(json.dumps(followers, indent=2))


def find_unfollowers(previous: dict, current: dict) -> list:
    """User IDs present before but missing now."""
    return [uid for uid in previous if uid not in current]


# ---------------------------------------------------------------------------
# Google Sheets export
# ---------------------------------------------------------------------------
def export_to_google_sheets(rows: list) -> None:
    """rows: list of (timestamp, user_id, username) tuples."""
    if not rows:
        return
    if not GOOGLE_SHEET_ID:
        print("GOOGLE_SHEET_ID not set — skipping Sheets export. Rows:")
        for r in rows:
            print("  ", r)
        return

    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(GOOGLE_SHEET_ID)

    try:
        ws = sh.worksheet(GOOGLE_SHEET_TAB)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=GOOGLE_SHEET_TAB, rows=1000, cols=3)
        ws.append_row(["Detected At (UTC)", "User ID", "Username"])

    ws.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"Appended {len(rows)} unfollower(s) to Google Sheet.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    client = get_client()
    user_id = resolve_user_id(client)

    print("Fetching current followers from X...")
    current_followers = fetch_followers(client, user_id)
    print(f"Found {len(current_followers)} current followers.")

    previous_followers = load_previous_snapshot()

    if not previous_followers:
        print("No previous snapshot found — this is the first run. "
              "Saving baseline snapshot, nothing to compare yet.")
        save_snapshot(current_followers)
        return

    unfollower_ids = find_unfollowers(previous_followers, current_followers)

    if not unfollower_ids:
        print("No unfollowers detected since last run.")
    else:
        timestamp = datetime.now(timezone.utc).isoformat()
        rows = [
            [timestamp, uid, previous_followers.get(uid, "unknown")]
            for uid in unfollower_ids
        ]
        print(f"Detected {len(rows)} unfollower(s):")
        for _, uid, uname in rows:
            print(f"  - @{uname} (id: {uid})")
        export_to_google_sheets(rows)

    save_snapshot(current_followers)


if __name__ == "__main__":
    main()
