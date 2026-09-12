# X Unfollower Tracker

Tracks who unfollows you on X (Twitter) and logs them to a Google Sheet.

Each run snapshots your current follower list, diffs it against the last
snapshot, and appends any newly-detected unfollowers to a Google Sheet with
a timestamp.

## How it works

1. Fetches your current followers via the X API v2.
2. Compares them against `followers_snapshot.json` (saved locally from the
   previous run).
3. Anyone present in the old snapshot but missing from the new one is
   logged as an unfollower.
4. Appends those rows to a Google Sheet (or prints them if Sheets isn't
   configured yet).
5. Saves the current follower list as the new snapshot.

The **first run only establishes a baseline** — there's nothing to compare
against yet, so no unfollowers will be reported until the second run.

## Requirements

- Python 3.9+
- An X (Twitter) developer account with **at least Basic-tier API access**.
  The free tier does not expose the followers endpoint at usable limits.
- A Google Cloud service account with the Sheets and Drive APIs enabled
  (only needed if you want the Sheets export, rather than console output).

## Setup

### 1. Install dependencies

```bash
pip install tweepy gspread google-auth
```

### 2. X API credentials

1. Create a project/app at [developer.x.com](https://developer.x.com).
2. Generate a Bearer Token.
3. Find your numeric user ID (or just use your @handle).

### 3. Google Sheets credentials (optional but recommended)

1. Create a service account in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Sheets API** and **Google Drive API** for the project.
3. Create a JSON key for the service account and download it.
4. Open your target Google Sheet and share it with the service account's
   email address (found in the JSON key as `client_email`), with Editor
   access.
5. Copy the spreadsheet ID from its URL:
   `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

### 4. Environment variables

```bash
export X_BEARER_TOKEN="your-bearer-token"
export X_USER_ID="your-numeric-user-id"      # or use X_USERNAME instead
# export X_USERNAME="your_handle"            # alternative to X_USER_ID

export GOOGLE_SERVICE_ACCOUNT_FILE="/path/to/service_account.json"
export GOOGLE_SHEET_ID="your-spreadsheet-id"
# export GOOGLE_SHEET_TAB="Unfollowers"      # optional, defaults to "Unfollowers"
```

## Usage

```bash
python x_unfollower_tracker.py
```

Run it again later (next day, next week, whatever cadence you want) to see
newly-detected unfollowers appended to the sheet.

### Automating it

To track unfollowers over time, schedule the script to run periodically.

**Cron (Linux/macOS)**, e.g. daily at 9am:

```cron
0 9 * * * cd /path/to/script && /usr/bin/python3 x_unfollower_tracker.py >> tracker.log 2>&1
```

**Windows Task Scheduler**: create a daily task that runs
`python x_unfollower_tracker.py` in the script's directory.

## Files

| File                        | Purpose                                             |
|-----------------------------|------------------------------------------------------|
| `x_unfollower_tracker.py`   | Main script                                          |
| `followers_snapshot.json`   | Auto-generated — your last known follower list       |
| `service_account.json`      | Your Google service account key (not committed)      |

## Notes & limitations

- X API rate limits apply; large follower counts may take a while to
  paginate through (`wait_on_rate_limit=True` handles this automatically).
- The script only detects unfollows *between runs* — if someone follows and
  unfollows in between two runs, it won't be caught.
- Keep `followers_snapshot.json` and your service account key **out of
  version control** (see `.gitignore` below).

## .gitignore

```
followers_snapshot.json
service_account.json
*.log
__pycache__/
```

## License

MIT — do whatever you want with it.
