---
name: database-performance
description: Use when a database is the bottleneck. Covers finding the expensive queries, index strategy, lock contention, connection saturation, and the schema decisions that make queries fast or impossible.
metadata:
  category: data
  version: 1.0.0
  tags: [performance, indexing, locks, query-optimization, scaling]
---

# Database Performance

## Purpose

Make the database fast by finding what it is actually spending time on. Database performance work fails when it starts from intuition; it succeeds when it starts from `EXPLAIN ANALYZE` and the slow-query log.

## When to Use

- An endpoint is slow and the database is suspected.
- CPU or I/O on the database server is saturated.
- Lock waits, timeouts, or deadlocks in production.
- Planning for a tenfold increase in data volume.

## Capabilities

- Query profiling and execution-plan analysis.
- Index strategy: what to add, and what to remove.
- Lock contention and deadlock diagnosis.
- Connection pool sizing.
- Denormalization, materialization, and partitioning as scaling tools.

## Inputs

- The slow query log, or the top queries by total execution time.
- Actual execution plans, with row counts.
- Table sizes, index sizes, and hardware.

## Outputs

- The identified bottleneck, with evidence.
- A change — index, query rewrite, or schema — and its measured effect.
- Monitoring so the regression is caught next time.

## Workflow

1. **Rank by total time, not by mean** — The query taking 20ms and running 50,000 times per minute is the problem. The 3-second report that runs hourly is not.
2. **Read the plan** — `EXPLAIN (ANALYZE, BUFFERS)`. Look for: a sequential scan on a large table, an estimate that differs from the actual by more than 10x, and a nested loop over many rows.
3. **Fix the biggest thing** — Usually a missing index, an N+1 from the application, or a query that fetches far more rows than it uses.
4. **Check the locks** — If queries are fast in isolation but slow in production, the problem is contention, not the plan. Look at lock waits and long-running transactions.
5. **Size the pool correctly** — More connections is not more throughput. Beyond the point where the database is saturated, additional connections increase latency for everyone.
6. **Re-measure under production-like load** — A query that is fast on a warm cache with 10,000 rows tells you nothing about 10 million.

## Best Practices

- The N+1 query is the most common database performance defect in application code, and it is invisible in the database's own metrics — it looks like a lot of fast queries. Count queries per request.
- An index makes reads faster and every write slower. A table with fifteen indexes has a write path that is fifteen times more expensive than it needs to be.
- `SELECT *` prevents index-only scans and transfers columns nobody uses. On a wide table this is a significant, invisible cost.
- A long-running transaction blocks vacuum, holds locks, and can stall an entire migration. Keep transactions short — and never open one around an HTTP call.
- Connection pool size should be roughly `(core_count * 2) + effective_spindle_count`, not "as many as the application can open". A pool of 500 against an 8-core database is a queue with extra steps.
- Denormalize deliberately, with a plan for keeping the copy consistent. An unmaintained denormalized column is a bug that reports itself as a customer complaint.

## Examples

**Reading a plan for what is actually wrong:**

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT o.id, o.total_cents, c.name
FROM orders o JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'open' AND o.created_at > now() - interval '7 days'
ORDER BY o.created_at DESC LIMIT 50;
```

```text
Limit  (cost=284913.42..284919.26 rows=50) (actual time=3184.221..3184.238 rows=50 loops=1)
  ->  Sort  (actual time=3184.219..3184.229 rows=50 loops=1)
        Sort Method: top-N heapsort  Memory: 32kB
        ->  Hash Join  (actual time=812.4..3102.8 rows=48,213 loops=1)
              ->  Seq Scan on orders o  (actual time=0.9..2894.1 rows=48,213 loops=1)
                    Filter: ((status = 'open') AND (created_at > ...))
                    Rows Removed by Filter: 8,214,502          <-- reading 8.2M rows
                    Buffers: shared read=184,221               <-- ~1.4 GB from disk
Planning Time: 0.4 ms
Execution Time: 3184.9 ms
```

The diagnosis is in "Rows Removed by Filter": Postgres read 8.2 million rows to return 50. The fix is an index that matches the filter *and* the sort:

```sql
CREATE INDEX CONCURRENTLY idx_orders_open_recent
  ON orders (created_at DESC)
  WHERE status = 'open';
-- Execution time: 3184ms -> 1.8ms. The partial index is also small enough
-- to stay entirely in cache.
```

**Finding an N+1 from the application side:**

```python
# The database sees 201 fast queries and reports no problem.
# The endpoint takes 900ms. Count queries per request to see it.
with query_counter() as counted:
    response = client.get("/orders")
assert counted.total <= 3, f"N+1 detected: {counted.total} queries for one request"
```

## Notes

- An index that matches both the `WHERE` and the `ORDER BY` lets the database skip sorting entirely. This is frequently the difference between 3 seconds and 2 milliseconds, and it is why column order in the index matters.
- Deadlocks are almost always caused by two transactions acquiring the same locks in different orders. Fix the ordering; retry logic only papers over it.
- Adding read replicas does not fix a slow query — it just runs the slow query on more machines. Fix the query first.
