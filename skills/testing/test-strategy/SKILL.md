---
name: test-strategy
description: Use when deciding what to test and at which level. Covers the test pyramid, what belongs in unit versus integration versus end-to-end tests, coverage as a signal rather than a target, and eliminating flakiness.
metadata:
  category: testing
  version: 1.0.0
  tags: [testing, strategy, pyramid, coverage, flakiness]
---

# Test Strategy

## Purpose

Build a test suite that catches real defects, runs fast enough to be run, and does not need to be rewritten every time the code is refactored.

## When to Use

- Designing a test suite for a new project.
- A suite that is slow, flaky, or fails to catch bugs.
- Deciding what to test for a specific change.
- Setting a coverage policy without making coverage the goal.

## Capabilities

- Test-level selection: unit, integration, contract, end-to-end.
- Test-double strategy: what to fake, what to use for real.
- Coverage interpretation.
- Flakiness diagnosis and elimination.
- Suite performance: parallelization and selective execution.

## Inputs

- The system, its dependencies, and its risk profile.
- The current suite: its runtime, its failure rate, its bug-escape rate.

## Outputs

- A test suite whose distribution across levels is deliberate.
- A fast feedback loop for the tests run on every change.
- Zero tolerated flakes.

## Workflow

1. **Test behavior, not implementation** — A test that breaks when you rename a private method is a test that prevents refactoring rather than enabling it.
2. **Choose the level by what you are verifying** — Business logic: unit tests, fast and many. Integration with a real database or queue: integration tests, fewer. A complete user journey: end-to-end, a handful.
3. **Use real dependencies where practical** — A test against a real Postgres in a container catches the SQL error that a mocked repository never will. Mocks verify that you called a thing; they do not verify that it works.
4. **Write the test that would have caught the bug** — After every production defect. This is where the highest-value tests come from — a real bug is empirical evidence of an untested path.
5. **Treat a flake as a defect** — Quarantine it immediately, then fix it. A suite with a 2% flake rate teaches the team to re-run and eventually to ignore.
6. **Keep the fast loop fast** — Under five minutes for what runs on every change, or people will stop running it.

## Best Practices

- Coverage is a signal, not a target. 100% coverage with assertion-free tests catches nothing; 60% coverage on the paths that matter catches most things. Look at what is *not* covered, not at the number.
- The most valuable tests are at the boundaries: the empty list, the null, the concurrent write, the network failure. The happy path is the one that already works.
- Mock what you do not own (a third-party payment API); use the real thing for what you do (your own database). Mocking your own repository layer tests only that your mock is configured correctly.
- A test that requires a comment to explain what it is testing is testing too much.
- Never assert on a log message or an internal call count unless that *is* the contract. Those assertions break on every refactor and catch nothing.
- Delete tests that no longer earn their keep. A test suite is code and carries maintenance cost.

## Examples

**A test that verifies behavior, and one that verifies implementation:**

```python
# Bad: verifies the implementation. Breaks on any refactor; catches no bugs.
def test_refund_calls_gateway():
    gateway = Mock()
    RefundService(gateway).refund(order, 1000)
    gateway.refund.assert_called_once_with(order.charge_id, 1000)
    # This passes even if the refund is never recorded, the amount is wrong
    # in the database, and the customer is charged again.

# Good: verifies the behavior that the user and the business care about.
def test_refund_reduces_balance_and_is_idempotent(db, fake_gateway):
    order = place_order(db, total_cents=5_000)
    service = RefundService(fake_gateway, db)

    result = service.refund(order.id, amount_cents=2_000)

    assert result.ok
    assert db.orders.get(order.id).refunded_cents == 2_000
    assert fake_gateway.total_refunded(order.charge_id) == 2_000

    # The same request again must not refund twice.
    service.refund(order.id, amount_cents=2_000, idempotency_key=result.key)
    assert db.orders.get(order.id).refunded_cents == 2_000
```

**The distribution that actually works:**

```text
Unit          ~70%   milliseconds each   business logic, edge cases, error paths
Integration   ~25%   seconds each        real DB, real queue, real HTTP layer
End-to-end     ~5%   tens of seconds     the three journeys that must never break

The proportions matter less than the principle: put the volume where the tests
are fast and the coverage is cheap, and reserve the slow, brittle level for
the handful of paths whose failure would be catastrophic.
```

## Notes

- Testcontainers gives you a real database, queue, or cache per test run, in Docker. It has largely eliminated the argument for mocking your own infrastructure — the real thing is now nearly as easy.
- Contract tests (Pact and similar) verify that two services agree on their interface without deploying both. They are the right tool when end-to-end tests across services have become the bottleneck.
- A test suite that has never caught a bug in production code is either a very good sign or a very bad one. Check which by mutating the code and seeing whether the tests notice.
