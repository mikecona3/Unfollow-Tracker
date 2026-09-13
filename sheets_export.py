"""
Shared Google Sheets export helper. Each platform writes to its own tab
in the same spreadsheet so both can be tracked side by side.
"""

from .config import config


def _get_worksheet(sheet_tab: str, header: list):
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(
        config.google_service_account_file, scopes=scopes
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(config.google_sheet_id)

    try:
        ws = sh.worksheet(sheet_tab)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=sheet_tab, rows=1000, cols=len(header))
        ws.append_row(header)
    return ws


def export_x_rows(rows: list) -> None:
    if not rows:
        return
    if not config.google_sheet_id:
        print("GOOGLE_SHEET_ID not set — skipping Sheets export. X unfollower rows:")
        for r in rows:
            print("  ", r)
        return

    ws = _get_worksheet(
        config.google_sheet_tab_x, ["Detected At (UTC)", "User ID", "Username"]
    )
    ws.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"Appended {len(rows)} X unfollower(s) to Google Sheet.")


def export_instagram_rows(rows: list) -> None:
    if not rows:
        return
    if not config.google_sheet_id:
        print("GOOGLE_SHEET_ID not set — skipping Sheets export. Instagram count rows:")
        for r in rows:
            print("  ", r)
        return

    ws = _get_worksheet(
        config.google_sheet_tab_instagram,
        ["Checked At (UTC)", "Follower Count", "Change Since Last Run"],
    )
    ws.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"Appended {len(rows)} Instagram follower-count row(s) to Google Sheet.")
