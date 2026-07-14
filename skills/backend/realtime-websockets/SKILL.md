---
name: realtime-websockets
description: Use when building realtime features with WebSockets or Server-Sent Events. Covers protocol choice, connection lifecycle, reconnection and backfill, scaling across instances, and backpressure.
metadata:
  category: backend
  version: 1.0.0
  tags: [websockets, sse, realtime, scaling, backpressure]
---

# Realtime and WebSockets

## Purpose

Build realtime features that behave correctly when the connection drops — which it will, constantly, on mobile networks. The hard part is not the socket; it is the state after the reconnect.

## When to Use

- Building live updates, chat, presence, collaborative editing, or streaming dashboards.
- Choosing between WebSockets, SSE, and polling.
- Scaling a socket server beyond one instance.
- Diagnosing memory growth or dropped messages under load.

## Capabilities

- Protocol selection and trade-offs.
- Connection lifecycle: handshake, auth, heartbeat, graceful close.
- Reconnection with resume tokens and gap backfill.
- Horizontal scaling with a pub/sub fan-out layer.
- Backpressure and slow-consumer handling.

## Inputs

- Direction of data flow (server to client, or bidirectional).
- Message volume, size, and acceptable latency.
- Whether missed messages must be recovered or can be dropped.

## Outputs

- A protocol choice with a stated reason.
- A reconnect path that restores correct state, not just a live socket.
- A scaling design that works with more than one server instance.

## Workflow

1. **Choose the simplest protocol that works** — Server-to-client only? Use SSE: it is plain HTTP, reconnects automatically, and passes through proxies. Bidirectional and low-latency? WebSockets. Infrequent updates? Polling is not embarrassing.
2. **Authenticate at the handshake** — Validate the token on connect; re-validate periodically for long-lived sockets. A socket opened an hour ago may belong to a revoked session.
3. **Heartbeat both ways** — Ping/pong with a timeout. Without it, half-open connections accumulate and leak memory for hours.
4. **Design the resume** — Every message carries a monotonic sequence number. On reconnect, the client sends its last-seen ID; the server replays the gap or tells it to resynchronize fully.
5. **Fan out via pub/sub** — With more than one instance, a message published on instance A must reach a client connected to instance B. Redis pub/sub, NATS, or the broker you already have.
6. **Apply backpressure** — Bound the per-connection send buffer. When it fills, drop the slow consumer rather than the server.

## Best Practices

- The reconnect path is the feature. Test it by killing the connection mid-stream, not by refreshing the page.
- Never trust the client's claimed last-seen sequence without bounding the replay. A malicious or buggy client can request a million-message backfill.
- Reconnect with exponential backoff and jitter. A server restart otherwise brings every client back simultaneously and takes it down again.
- Sticky sessions are a workaround, not a design. Make any instance able to serve any client.
- An unbounded outbound queue per connection is a memory leak with a slow client attached to it.
- Send binary or compact JSON; per-message overhead dominates at high message rates.

## Examples

**Resumable stream with sequence numbers:**

```typescript
// Client
const ws = new WebSocket(`${URL}?resume_from=${lastSeq ?? ""}`);

ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.seq !== lastSeq + 1 && lastSeq !== null) {
    // Gap detected: the server could not replay. Resynchronize from scratch.
    return resyncFromSnapshot();
  }
  lastSeq = msg.seq;
  apply(msg);
};

ws.onclose = () => scheduleReconnect(backoff.next()); // exponential + jitter
```

```typescript
// Server: replay bounded, or instruct a full resync
const from = Number(url.searchParams.get("resume_from"));
const gap = currentSeq - from;

if (Number.isFinite(from) && gap > 0 && gap <= MAX_REPLAY) {
  for (const msg of await log.range(from + 1, currentSeq)) send(socket, msg);
} else {
  send(socket, { type: "resync_required", seq: currentSeq });
}
```

## Notes

- SSE is limited to six concurrent connections per domain on HTTP/1.1 browsers. Over HTTP/2 this limit effectively disappears — check what your load balancer actually terminates.
- Load balancers commonly kill idle connections after 60 seconds. Your heartbeat interval must be shorter than the shortest idle timeout in the path.
- For collaborative editing, message replay is not enough — you need CRDTs or operational transformation. Sequence numbers give you delivery, not convergence.
