---
name: legacy-modernization
description: Use when incrementally modernizing a legacy system without a rewrite. Covers characterization tests, seams, the strangler pattern, and sequencing migrations so the system stays shippable throughout.
metadata:
  category: development
  version: 1.0.0
  tags: [legacy, migration, strangler-pattern, refactoring]
---

# Legacy Modernization

## Purpose

Replace a legacy system incrementally, keeping it in production the entire time. The failure mode this skill exists to prevent is the two-year rewrite that ships nothing and is cancelled.

## When to Use

- A system that works but resists change.
- Migrating off an unsupported framework, runtime, or vendor.
- Extracting a service from a monolith.
- Any proposal that starts with "we should just rewrite it".

## Capabilities

- Characterization testing to capture undocumented behavior.
- Seam identification and dependency breaking.
- Strangler-fig migration behind a routing facade.
- Data migration with dual writes and backfills.
- Sequencing work so every step is independently shippable.

## Inputs

- The legacy system, its deployment, and its actual traffic patterns.
- The concrete pain: what change is expensive, and how expensive.
- Constraints: uptime requirements, data volume, compliance, team capacity.

## Outputs

- A migration plan of independently shippable increments.
- Characterization tests covering the behavior being preserved.
- A facade or router that lets old and new coexist.
- A decommissioning checklist for the old path.

## Workflow

1. **Resist the rewrite** — Establish what the current system does that a rewrite would have to rediscover. This list is always longer than expected, and it is the argument.
2. **Pin the behavior** — Characterization tests at the outermost boundary you can reach: HTTP, CLI, batch output. Record what it does, bugs included.
3. **Introduce a facade** — Put a routing layer in front of the capability. Every request now flows through a point you control.
4. **Carve off one capability** — Choose the smallest one with clear boundaries. Implement it in the new system. Route a percentage of traffic to it.
5. **Compare, then cut over** — Run both and diff the outputs (shadow mode) until you trust the new path. Then flip the route.
6. **Delete the old path** — Immediately. A migration that leaves both paths alive has doubled the maintenance burden, not reduced it.
7. **Repeat** — Next capability. Each cycle ships.

## Best Practices

- Never begin by changing the database. Data is the hardest thing to migrate and the least reversible — do it last, or behind a repository interface.
- Shadow traffic is the cheapest confidence you will ever buy. Send real requests to the new path, discard its response, and compare.
- Feature-flag every cutover so the rollback is a config change, not a deploy.
- Migrate the highest-churn code first. The legacy code nobody has touched in three years is not what is slowing you down.
- Keep a written kill list of old code paths, and cross them off. Otherwise the "temporary" fallback lives forever.
- Do not modernize style, structure, and behavior at once. Preserve behavior; the rest can follow.

## Examples

**Strangler routing with shadow comparison:**

```python
async def get_pricing(request: PricingRequest) -> Pricing:
    legacy_result = await legacy_pricing.calculate(request)

    if flags.enabled("pricing.shadow", request.tenant_id):
        try:
            new_result = await pricing_service.calculate(request)
            if new_result != legacy_result:
                logger.warning(
                    "pricing_mismatch",
                    extra={"tenant": request.tenant_id,
                           "legacy": legacy_result.total_cents,
                           "new": new_result.total_cents},
                )
        except Exception:
            logger.exception("shadow_pricing_failed")  # never affects the response

    if flags.enabled("pricing.cutover", request.tenant_id):
        return await pricing_service.calculate(request)

    return legacy_result
```

Shadow mode surfaces every discrepancy on real traffic before a single user is affected by the new path.

## Notes

- A mismatch rate that will not converge to zero usually means the legacy behavior is not what the spec says. The legacy behavior is the spec.
- Dual-writing to two data stores requires an idempotency key and a reconciliation job. Without both, they will drift.
- The decommission is part of the project. A migration is not done when the new path serves traffic; it is done when the old code is deleted.
