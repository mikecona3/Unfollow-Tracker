# Unfollower Tracker

Tracks who unfollows you on **X (Twitter)**, and/or your **Instagram**
follower count over time. Choose either platform, or both, per run.

## Important: X vs. Instagram are not equivalent

| Platform  | What you get                                      | Why |
|-----------|----------------------------------------------------|-----|
| **X**       | A real list of **who** unfollowed you (username + ID) | X's API exposes an actual follower list |
| **Instagram** | Only your follower **count** and how it changed run-to-run | Meta's official Graph API does **not** expose individual follower usernames — only aggregate metrics |

Getting actual Instagram follower *usernames* would require unofficial
private-API libraries (e.g. `instagrapi`) or browser automation, both of
which violate Instagram's Terms of Service and risk the account being
rate-limited or banned. This project intentionally does not do that — it
only uses Meta's sanctioned Graph API, which caps what's available to
count-level tracking.

## How it works

Each run, per selected platform:

1. Fetches current data (follower list for X, follower count for
   Instagram) from the platform's official API.
2. Compares it to a local JSON snapshot saved from the previous run
   (`x_snapshot.json` / `instagram_snapshot.json`).
3. For X: anyone in the old snapshot but missing now is logged as an
   unfollower.
   For Instagram: the numeric change in follower count is logged.
4. Appends the results to a Google Sheet (X and Instagram get separate
   tabs in the same spreadsheet), or prints them if Sheets isn't
   configured.
5. Saves current data as the new snapshot.

**The first run per platform only establishes a baseline** — nothing is
reported as changed until the second run.

## Requirements

- Python 3.9+
- **For X**: a developer account with at least **Basic-tier** API access
  (the free tier doesn't expose the followers endpoint at usable limits).
- **For Instagram**: a Business or Creator account connected to a Facebook
  Page, and a Graph API access token with `instagram_basic` permission.
- **For Sheets export** (optional): a Google Cloud service account with the
  Sheets and Drive APIs enabled.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. X API credentials (skip if you only want Instagram)

1. Create a project/app at [developer.x.com](https://developer.x.com).
2. Generate a Bearer Token.
3. Find your numeric user ID (or just use your @handle).

### 3. Instagram API credentials (skip if you only want X)

1. Convert your Instagram account to a Business or Creator account and
   connect it to a Facebook Page (required by Meta for API access).
2. Create an app at [developers.facebook.com](https://developers.facebook.com).
3. Generate a long-lived Graph API access token with the
   `instagram_basic` permission for that account.
4. Find your Instagram Business Account ID (available via the Graph API
   Explorer or your Facebook Page's connected-account settings).

### 4. Google Sheets credentials (optional but recommended)

1. Create a service account in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Sheets API** and **Google Drive API**.
3. Download the service account's JSON key.
4. Share your target Google Sheet with the service account's email
   (the `client_email` field in the JSON key), with Editor access.
5. Copy the spreadsheet ID from its URL:
   `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

### 5. Environment variables

```bash
# X (Twitter) — omit if not tracking X
export X_BEARER_TOKEN="your-bearer-token"
export X_USER_ID="your-numeric-user-id"      # or use X_USERNAME instead
# export X_USERNAME="your_handle"

# Instagram — omit if not tracking Instagram
export IG_ACCESS_TOKEN="your-graph-api-token"
export IG_BUSINESS_ACCOUNT_ID="your-ig-business-account-id"

# Google Sheets — omit to just print results to the console instead
export GOOGLE_SERVICE_ACCOUNT_FILE="/path/to/service_account.json"
export GOOGLE_SHEET_ID="your-spreadsheet-id"
# export GOOGLE_SHEET_TAB_X="X Unfollowers"                    # optional
# export GOOGLE_SHEET_TAB_INSTAGRAM="Instagram Follower Counts" # optional

# Optional: where local snapshot files are stored (defaults to cwd)
# export SNAPSHOT_DIR="/path/to/data"
```

You only need to set credentials for the platform(s) you actually use —
the tool skips a platform gracefully (with a clear message) if its
credentials aren't set, rather than crashing.

## Usage

```bash
python -m unfollower_tracker --platform x            # X only
python -m unfollower_tracker --platform instagram     # Instagram only
python -m unfollower_tracker --platform both          # both (default)
python -m unfollower_tracker                          # same as --platform both
```

Run it again later (next day, next week, whatever cadence) to see changes
show up.

### Automating it

**Cron (Linux/macOS)**, e.g. daily at 9am:

```cron
0 9 * * * cd /path/to/unfollower_tracker && /usr/bin/python3 -m unfollower_tracker --platform both >> tracker.log 2>&1
```

**Windows Task Scheduler**: create a daily task running
`python -m unfollower_tracker --platform both` from the project directory.

## Project structure

```
unfollower_tracker/
├── unfollower_tracker/
│   ├── __init__.py
│   ├── __main__.py          # enables `python -m unfollower_tracker`
│   ├── main.py               # CLI entry point / argument parsing
│   ├── config.py              # env var loading + validation
│   ├── snapshot.py            # shared JSON snapshot save/load
│   ├── sheets_export.py       # shared Google Sheets export
│   └── providers/
│       ├── __init__.py
│       ├── x_provider.py         # X follower list + diff
│       └── instagram_provider.py # Instagram follower count + diff
├── requirements.txt
└── README.md
```

## Files generated at runtime (not committed)

| File                          | Purpose                                        |
|--------------------------------|-------------------------------------------------|
| `x_snapshot.json`              | Last known X follower list                     |
| `instagram_snapshot.json`      | Last known Instagram follower count             |
| `service_account.json`         | Your Google service account key                |

## .gitignore

```
*_snapshot.json
service_account.json
*.log
__pycache__/
*.pyc
```

## Notes & limitations

- X API rate limits apply for large follower counts; `wait_on_rate_limit=True`
  handles this automatically but large accounts may take a while.
- Both platforms only detect changes **between runs** — someone who follows
  and unfollows between two runs won't be caught.
- Instagram results are **counts only, never usernames** — see the table
  at the top of this README for why.

## License

MIT — do whatever you want with it.
