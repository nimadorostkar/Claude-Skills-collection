---
name: performance-testing
description: Use when load testing a system. Covers workload modeling, ramp profiles, what to measure, finding the breaking point, and distinguishing a real bottleneck from a badly configured test.
metadata:
  category: testing
  version: 1.0.0
  tags: [load-testing, performance, k6, benchmarking, capacity]
---

# Performance Testing

## Purpose

Find out where a system breaks, and why, before production finds out for you. A load test that reports "we handled 1,000 requests per second" without stating the latency, the error rate, and where the bottleneck was tells you nothing useful.

## When to Use

- Before a known traffic event: a launch, a campaign, a migration.
- Establishing a capacity baseline.
- Verifying that a performance fix worked.
- Finding the breaking point of a new service.

## Capabilities

- Workload modeling from real traffic patterns.
- Load profiles: smoke, load, stress, spike, soak.
- Measuring the right things: latency percentiles, error rate, saturation.
- Bottleneck identification across the stack.
- Result interpretation and capacity projection.

## Inputs

- Real traffic patterns: the mix of endpoints, the shape of the day, the payload sizes.
- The target: expected load, and the load you must survive.
- A production-like environment. A test against a laptop measures the laptop.

## Outputs

- The breaking point, and the component that broke.
- Latency percentiles at each load level, not an average.
- A capacity conclusion: what this system can serve, and where it needs work.

## Workflow

1. **Model the workload from reality** — Take the endpoint mix from production access logs. A test that hammers one endpoint measures that endpoint, not your system.
2. **Ramp, do not slam** — Start below expected load and increase gradually. The point at which latency starts climbing is more informative than the point at which it falls over.
3. **Measure percentiles, never averages** — An average latency of 200ms is consistent with half the users waiting 400ms. Report p50, p95, p99, and the maximum.
4. **Watch the system, not just the client** — CPU, memory, connection pools, database locks, queue depth. The load generator tells you what happened; the system tells you why.
5. **Find the first bottleneck, fix it, repeat** — There is always another one behind it. Performance testing is iterative.
6. **Soak test separately** — Run at moderate load for hours. Memory leaks, connection leaks, and disk-filling logs only appear over time.

## Best Practices

- Validate the load generator first. If the client saturates its own CPU or its ephemeral ports, you are measuring the test, not the system. This mistake is extremely common.
- An error rate above zero invalidates the throughput number. Serving 5,000 requests per second while failing 8% of them is serving 4,600 requests per second, badly.
- Test with realistic data volumes. A query that is fast against 10,000 rows tells you nothing about its behavior against 10 million.
- Include think time and connection churn. Real users pause; a test with zero think time and perfect connection reuse is an unrealistic best case.
- Never load test production without agreement, a plan, and an abort switch.
- Report the bottleneck, not just the number. "We hit 2,000 rps" is trivia. "We hit 2,000 rps, at which point the database connection pool saturated at 40 connections and p99 went to 4 seconds" is actionable.

## Examples

**A ramp profile that finds the knee, with thresholds that fail the test:**

```javascript
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    ramp: {
      executor: "ramping-arrival-rate",   // arrival rate: models users, not workers
      startRate: 50,
      timeUnit: "1s",
      preAllocatedVUs: 200,
      maxVUs: 2000,
      stages: [
        { target: 200,  duration: "3m" },   // expected peak
        { target: 500,  duration: "3m" },   // 2.5x
        { target: 1000, duration: "3m" },   // find the knee
        { target: 2000, duration: "3m" },   // find the wall
      ],
    },
  },
  thresholds: {
    // The test fails if these are breached. A load test with no thresholds is a demo.
    http_req_failed:   ["rate<0.01"],
    http_req_duration: ["p(95)<500", "p(99)<1500"],
  },
};

// The endpoint mix, taken from production access logs — not a single hot path.
export default function () {
  const r = Math.random();
  if (r < 0.62)      http.get(`${__ENV.BASE}/api/products`);
  else if (r < 0.85) http.get(`${__ENV.BASE}/api/products/${randomSku()}`);
  else if (r < 0.97) http.post(`${__ENV.BASE}/api/cart`, JSON.stringify(cartItem()));
  else               http.post(`${__ENV.BASE}/api/checkout`, JSON.stringify(order()));

  sleep(Math.random() * 3 + 1);            // think time: real users pause
}
```

**A result that is actually useful:**

```text
Breaking point: ~840 requests/second.

At 800 rps:  p50 42ms   p95 180ms   p99 410ms    errors 0.0%
At 900 rps:  p50 51ms   p95 890ms   p99 3,200ms  errors 0.4%
At 1000 rps: p50 2.1s   p95 8.4s    p99 timeout  errors 11%

Bottleneck: the Postgres connection pool saturates at 40 connections. Beyond
~840 rps, requests queue for a connection; the queue wait dominates the response
time entirely. Database CPU peaked at 34% — the database was never the limit,
the pool in front of it was.

Fix: raise the pool to 100 and add PgBouncer in transaction mode.
Retest: breaking point moves to ~2,900 rps, where the database CPU finally
becomes the constraint at 89%.

Capacity conclusion: 2,900 rps sustained, against an expected peak of 200.
Headroom is adequate for the launch.
```

## Notes

- The result above is the most common finding in real load tests: the bottleneck was a configured limit, not a resource limit. The database was almost idle while the application queued behind its own pool.
- Arrival-rate executors (`ramping-arrival-rate`) model users arriving independently of how fast the system responds. VU-based executors slow down when the system does, which hides the failure — it is the wrong model for finding a breaking point.
- A soak test is the only way to find a slow leak. Everything looks fine for twenty minutes.
