Wait Room and Search mechanisms fine-tuned:
1. Top Row Skipping Fixed: Removed `min(10, rows.count())` limit. Explicitly calls `Home` before scanning to ensure top row isn't skipped.
2. Endless Waterfall Loop Removed: Scaled down Phase A master scroll from 15 to 5 passes and entirely removed the 12-pass slow-scroll for missing songs. It will now instantly use explicit Search if not found in the initial DOM snapshot.

Ready to test 1058-1100 range.
