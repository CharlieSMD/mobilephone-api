#!/usr/bin/env python3
"""
Run colors backfill in small batches with delays until no more phones need updates.
"""

import sys
import time

# Ensure we can import backfill_colors from this directory
sys.path.append('/Users/shenmeidun/UoW_IT/COMPX576/MobilePhone/crawler')

from backfill_colors import ColorBackfiller  # type: ignore


def main():
    batch_size = 5
    sleep_between_batches = 12.0
    bf = ColorBackfiller()
    total_updated = 0
    batch_num = 0

    while True:
        targets = bf.get_targets(limit=batch_size)
        if not targets:
            print(f"No more phones missing colors. Total updated: {total_updated}")
            break

        batch_num += 1
        print(f"\n=== Batch {batch_num}: processing up to {len(targets)} phones ===")
        before = total_updated
        bf.backfill(limit=batch_size, dry_run=False)
        # We cannot directly know how many updated in this call; just wait and proceed
        # Sleep between batches to reduce rate-limiting
        time.sleep(sleep_between_batches)


if __name__ == '__main__':
    main()






