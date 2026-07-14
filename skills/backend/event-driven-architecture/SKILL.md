---
name: event-driven-architecture
description: Use when designing systems around events and message queues. Covers event schema design, delivery guarantees, idempotent consumers, ordering, dead-letter handling, and event sourcing.
metadata:
  category: backend
  version: 1.0.0
  tags: [events, kafka, queues, messaging, idempotency]
---

# Event-Driven Architecture

## Purpose

Design event flows that survive redelivery, reordering, and consumer failure — because all three will happen, and the broker's guarantees are weaker than most designs assume.

## When to Use

- Introducing a message broker or queue.
- Designing event schemas that other teams will consume.
- Debugging duplicate processing, lost messages, or stuck consumers.
- Evaluating event sourcing for a subsystem.

## Capabilities

- Event schema design and versioning.
- Delivery semantics: at-most-once, at-least-once, effectively-once.
- Idempotent consumer design.
- Ordering and partitioning strategy.
- Dead-letter queues, retry policies, and poison-message handling.
- Event sourcing and CQRS, and when the cost is justified.

## Inputs

- The events the domain actually produces, in the domain's language.
- The broker and its real guarantees (not its marketing).
- Consumer requirements: ordering, latency, replay.

## Outputs

- Versioned event schemas with a registry or equivalent.
- Consumers that are safe to run twice on the same message.
- Retry, DLQ, and replay procedures.

## Workflow

1. **Name events in the past tense** — `OrderPlaced`, `PaymentFailed`. An event is a fact that happened, not a command to do something.
2. **Design the payload for consumers you do not control** — Include enough context that a consumer does not have to call back for the basics; do not include so much that every field change breaks someone.
3. **Assume at-least-once** — Every consumer must be idempotent. Deduplicate on an event ID, or make the operation naturally idempotent.
4. **Partition for ordering** — Ordering is guaranteed only within a partition. Key by the entity whose order matters (usually the aggregate ID).
5. **Handle poison messages** — A message that always fails must land in a DLQ after N attempts, not retry forever and block the partition.
6. **Version from the start** — Additive changes only; a new required field is a new event version.

## Best Practices

- Exactly-once delivery does not exist across a network. Exactly-once *processing* is achievable with idempotent consumers, and that is where the effort belongs.
- Retry with exponential backoff and jitter. Fixed-interval retries from many consumers synchronize into a thundering herd.
- A consumer that retries a permanently failing message forever blocks every message behind it. Always cap attempts.
- Do not put large payloads on the bus. Publish a reference and let the consumer fetch — or accept the coupling knowingly.
- Events are a public contract. Removing a field breaks consumers you have never met.
- Log the event ID at every hop. Without it, tracing a lost message is archaeology.

## Examples

**Idempotent consumer keyed on event ID:**

```python
async def handle(event: Event, conn: Connection) -> None:
    async with conn.transaction():
        # Insert the marker first. If this event was already processed,
        # the unique constraint rejects it and we skip the side effect.
        inserted = await conn.execute(
            "INSERT INTO processed_events (event_id, consumer) VALUES ($1, $2) "
            "ON CONFLICT DO NOTHING RETURNING 1",
            event.id, CONSUMER_NAME,
        )
        if not inserted:
            logger.info("duplicate_event_skipped", extra={"event_id": event.id})
            return

        await apply_side_effect(event, conn)   # same transaction as the marker
```

The marker and the side effect commit together. Redelivery is a no-op; a crash mid-transaction rolls back both and the message is redelivered cleanly.

## Notes

- Kafka guarantees ordering per partition, not per topic. If two events for the same order land in different partitions, they can be processed out of order — key by order ID.
- A DLQ with no alerting and no replay tooling is a place where messages go to be forgotten. Build the replay path when you build the DLQ.
- Event sourcing is a large commitment: every schema change becomes a versioning problem for events you can never rewrite. Adopt it where the audit log *is* the product, not as a default persistence strategy.
