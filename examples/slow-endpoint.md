# Debugging a slow endpoint

**Skills loaded:** `database-performance`, then `postgres`
**Outcome:** 3,184ms → 1.8ms

---

## The request

> The `/orders` page takes about 3 seconds to load and I think it's the database. Can you speed it up?

## Without the skills

An agent with no skill loaded typically starts guessing: add an index on `status`, add caching, suggest pagination, propose a read replica. Some of these might help. None of them is derived from evidence, and the agent has not asked for any.

## What the skills changed

`database-performance` opens with a rule that inverts the default approach:

> **Measure, do not guess.** `EXPLAIN (ANALYZE, BUFFERS)`. Never optimize a query you have not profiled.

So the agent asked for the plan instead of proposing a fix.

## The session

**Agent:** Before changing anything — can you run the query with `EXPLAIN (ANALYZE, BUFFERS)` and paste the output? Also, roughly how many rows are in `orders`?

**User:**

```
Limit  (cost=284913.42..284919.26 rows=50) (actual time=3184.221..3184.238 rows=50 loops=1)
  ->  Sort  (actual time=3184.219..3184.229 rows=50 loops=1)
        Sort Method: top-N heapsort  Memory: 32kB
        ->  Hash Join  (actual time=812.4..3102.8 rows=48213 loops=1)
              ->  Seq Scan on orders o  (actual time=0.9..2894.1 rows=48213 loops=1)
                    Filter: ((status = 'open') AND (created_at > (now() - '7 days'::interval)))
                    Rows Removed by Filter: 8214502
                    Buffers: shared read=184221
Execution Time: 3184.9 ms
```

8.3M rows in the table.

**Agent:** The finding is `Rows Removed by Filter: 8,214,502`.

Postgres read 8.2 million rows — about 1.4 GB from disk, per the `Buffers` line — to return 50. There is no index serving this query, so it scans the whole table, filters, then sorts.

Three things matter for the fix, and the third is the one usually missed:

1. The filter is on `status` and `created_at`.
2. `status = 'open'` is highly selective — most orders are not open.
3. **The query also sorts by `created_at DESC`.** An index that matches the filter but not the sort still requires a sort of every matching row.

A partial index on `created_at DESC`, restricted to open orders, serves the filter *and* the sort — the database can walk the index in order and stop after 50 rows.

```sql
CREATE INDEX CONCURRENTLY idx_orders_open_recent
  ON orders (created_at DESC)
  WHERE status = 'open';
```

`CONCURRENTLY` because this is a large production table — the plain form locks writes for the duration of the build.

**User:** Done.

```
Limit  (actual time=0.031..1.802 rows=50 loops=1)
  ->  Nested Loop  (actual time=0.029..1.771 rows=50 loops=1)
        ->  Index Scan using idx_orders_open_recent on orders o
              (actual time=0.019..0.204 rows=50 loops=1)
              Buffers: shared hit=54
Execution Time: 1.847 ms
```

**Agent:** 3,184ms → 1.8ms, a factor of about 1,700.

The plan now walks the index in sort order and stops at 50 rows. `Buffers: shared hit=54` — it reads 54 pages from cache instead of 184,221 from disk. The partial index is also small (only open orders), so it stays resident in memory.

Two follow-ups, from `postgres`:

- **Check for now-redundant indexes.** If there is an existing index on `orders (status)` alone, it is probably unused now and is costing you on every write. `pg_stat_user_indexes` will show whether it has ever been scanned.
- **This query is now fast; the endpoint may not be.** If the page issues one query per order to fetch the customer, that is an N+1 and it is invisible in the database's own metrics — it looks like a lot of fast queries. Count queries per request.

---

## What the skills contributed

| Step | Skill | The rule that fired |
| --- | --- | --- |
| Asked for the plan before proposing anything | `database-performance` | *Never optimize a query you have not profiled.* |
| Read `Rows Removed by Filter` as the finding | `database-performance` | *Look for a sequential scan on a large table and estimates that diverge from actuals.* |
| Indexed the sort, not only the filter | `database-performance` | *An index that matches both the `WHERE` and the `ORDER BY` lets the database skip sorting entirely.* |
| Used `CONCURRENTLY` | `postgres` | *`CREATE INDEX CONCURRENTLY` in production; the plain form locks writes.* |
| Flagged the possible N+1 | `database-performance` | *The N+1 is invisible in the database's own metrics — it looks like a lot of fast queries.* |

The 1,700× improvement came from the third row. An agent that indexed `(status, created_at)` in the wrong column order, or indexed only `status`, would have produced a real improvement and left most of it on the table.
