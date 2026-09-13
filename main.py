#!/usr/bin/env python3
"""
Unfollower Tracker
==================
Tracks who unfollows you on X, and/or your Instagram follower count over
time. See README.md for full setup instructions.

Usage:
    python -m unfollower_tracker --platform x
    python -m unfollower_tracker --platform instagram
    python -m unfollower_tracker --platform both
"""

import argparse
import sys

from .config import ConfigError
from .sheets_export import export_instagram_rows, export_x_rows


def run_x() -> None:
    from .providers import x_provider

    print("=== X (Twitter) ===")
    try:
        result = x_provider.run()
    except ConfigError as e:
        print(f"Skipping X: {e}")
        return

    print(f"Current followers: {result['follower_count']}")
    if result["first_run"]:
        print("No previous snapshot found — baseline saved. "
              "Run again later to detect unfollowers.")
        return

    if not result["unfollowers"]:
        print("No unfollowers detected since last run.")
    else:
        print(f"Detected {len(result['unfollowers'])} unfollower(s):")
        for u in result["unfollowers"]:
            print(f"  - @{u['username']} (id: {u['user_id']})")
        export_x_rows(result["sheet_rows"])


def run_instagram() -> None:
    from .providers import instagram_provider

    print("=== Instagram ===")
    print("Note: Instagram's official API only exposes follower COUNTS, "
          "not who specifically unfollowed you.")
    try:
        result = instagram_provider.run()
    except ConfigError as e:
        print(f"Skipping Instagram: {e}")
        return

    print(f"Current follower count: {result['follower_count']}")
    if result["first_run"]:
        print("No previous snapshot found — baseline saved. "
              "Run again later to see the change over time.")
        return

    delta = result["delta"]
    if delta == 0:
        print("No change in follower count since last run.")
    elif delta > 0:
        print(f"Gained {delta} follower(s) since last run.")
    else:
        print(f"Lost {abs(delta)} follower(s) since last run.")
    export_instagram_rows(result["sheet_rows"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Track unfollowers on X and/or Instagram.")
    parser.add_argument(
        "--platform",
        choices=["x", "instagram", "both"],
        default="both",
        help="Which platform(s) to check (default: both).",
    )
    args = parser.parse_args()

    if args.platform in ("x", "both"):
        run_x()
    if args.platform in ("instagram", "both"):
        run_instagram()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # top-level safety net so cron jobs log a clear error
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
