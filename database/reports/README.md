# Report Verification

Run schema, seed, views, functions, procedure, trigger and indexes in that order, then execute `queries/001_reports.sql`. Save results without private user data. For index evidence, compare `EXPLAIN (ANALYZE, BUFFERS)` before/after on a realistically sized test dataset; tiny seed data cannot prove performance.

