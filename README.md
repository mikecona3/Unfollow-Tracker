# Unfollow Tracker

Easily track who unfollows you on and log everything to a Google Sheet/Excel.

Every run snapshots your current follower list, diffs it against the previous
snapshot, and appends any newly-detected unfollowers to a Google Sheet

*NOTE: The first run only establishes a baseline - there's nothing to compare
against yet so no unfollowers will be reported. This is not an error, it is 
expected. Export will become available on the second run. 


## Setup

### 1. Install dependencies

bash
pip install tweepy gspread google-auth

### 2. X API credentials

1. Create a project/app at [developer.x.com](https://developer.x.com).
2. Generate a Bearer Token.
3. Find your numeric user ID (or just use your @handle).

### 3. Google Sheets credentials (recommended)

1. Create a service account in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Sheets API** and **Google Drive API** for the project.
3. Create a JSON key for the service account and download it.
4. Open your target Google Sheet and share it with the service account's
   email address (found in the JSON key as `client_email`), with Editor
   access.
5. Copy the spreadsheet ID from its URL:
   `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

### 4. Environment variables

bash
export X_BEARER_TOKEN="your-bearer-token"
export X_USER_ID="your-numeric-user-id"      # or use X_USERNAME instead
# export X_USERNAME="your_handle"            # alternative to X_USER_ID

export GOOGLE_SERVICE_ACCOUNT_FILE="/path/to/service_account.json"
export GOOGLE_SHEET_ID="your-spreadsheet-id"
# export GOOGLE_SHEET_TAB="Unfollowers"      # optional, defaults to "Unfollowers"


## Usage

bash
python x_unfollower_tracker.py
