---
name: network-troubleshooting
description: Use when diagnosing network failures: connection refused, timeouts, TLS errors, DNS problems, and intermittent failures. Covers layer-by-layer isolation and the tools that answer each question.
metadata:
  category: devops
  version: 1.0.0
  tags: [networking, dns, tls, debugging, connectivity]
---

# Network Troubleshooting

## Purpose

Isolate a network failure to a specific layer instead of guessing. Nearly every network problem is DNS, TLS, a firewall, or a timeout — and each has a distinct signature that identifies it in seconds.

## When to Use

- Connection refused, connection reset, or timeouts.
- TLS handshake and certificate errors.
- DNS resolution failures, including intermittent ones.
- "It works from my machine but not from the cluster."
- Intermittent failures under load.

## Capabilities

- Layer-by-layer isolation: DNS, TCP, TLS, HTTP.
- Tooling: `dig`, `nc`, `openssl s_client`, `curl -v`, `ss`, `tcpdump`.
- Cloud-specific diagnosis: security groups, NACLs, route tables, service meshes.
- Connection-pool and ephemeral-port exhaustion.
- MTU and path-MTU problems.

## Inputs

- The exact error message and the client that produced it.
- Where it fails from and where it succeeds from.
- Whether it is consistent or intermittent — this distinction matters more than any other.

## Outputs

- The failing layer, identified with evidence.
- The fix, and confirmation that the path now works from the failing location.

## Workflow

1. **Read the error precisely** — "Connection refused" means something is listening but rejecting, or nothing is there and the host answered. "Timeout" means nothing answered at all — usually a firewall dropping packets silently. These have completely different causes.
2. **Resolve the name** — `dig +short host`. If DNS is wrong or slow, nothing downstream matters. Check the resolver being used, not just your laptop's.
3. **Open a socket** — `nc -vz host port`. This separates "the network path is blocked" from "the application is broken", which is the single most valuable distinction available.
4. **Complete the handshake** — `openssl s_client -connect host:443 -servername host`. Certificate chain, expiry, and SNI problems all surface here.
5. **Make the request** — `curl -v`. Now, and only now, are you debugging the application.
6. **For intermittent failures, look at exhaustion** — Connection pools, ephemeral ports, conntrack tables, and DNS caches. Intermittent almost always means "a limit is being hit under load".

## Best Practices

- Test from the environment that is failing. A path that works from your laptop proves nothing about the path from a pod in a private subnet.
- Timeout means a packet was dropped, which means a firewall, security group, or NACL. Refused means a TCP RST, which means the host is reachable. Do not confuse them.
- Check both directions of a stateless NACL. A security group is stateful and permits the return path automatically; a NACL is not and does not.
- DNS in Kubernetes resolves through the cluster's resolver, with a search-path expansion that can generate five queries per lookup. A DNS problem in a cluster is rarely the same problem as on a laptop.
- An intermittent failure at exactly the same rate every time (say, 1 in 3) means a load balancer with one bad backend.
- `tcpdump` is the last resort and the final arbiter. When two layers disagree about what is happening, the packets do not lie.

## Examples

**Layer-by-layer isolation, run from inside the failing pod:**

```bash
# 1. DNS — does the name resolve, and to what?
dig +short api.internal.example.com
# empty  -> DNS failure. Check the resolver, the search path, the record itself.
# 10.0.4.17 -> continue.

# 2. TCP — is the path open at all?
nc -vz 10.0.4.17 8443
# "succeeded"          -> the path is open; the problem is above TCP.
# "Connection refused" -> reachable host, nothing listening on that port.
# hangs, then times out -> a firewall/security group/NACL is dropping. This is
#                          the most common cloud networking failure.

# 3. TLS — does the handshake complete, and is the chain valid?
openssl s_client -connect 10.0.4.17:8443 -servername api.internal.example.com </dev/null 2>&1 \
  | grep -E "Verify return code|subject=|issuer=|NotAfter"
# "unable to get local issuer certificate" -> missing intermediate, or the client
#                                             lacks the CA bundle.
# "certificate has expired"                -> it is 3am and it is the certificate.

# 4. HTTP — only now is it an application problem.
curl -v --max-time 5 https://api.internal.example.com/healthz
```

**Intermittent failure that is actually exhaustion:**

```bash
# Symptom: ~4% of outbound calls fail with "cannot assign requested address"
# under load, and never in staging.

ss -s
# TCP:   28901 (estab 210, closed 28180, timewait 28180/0)
#                                        ^^^^^ ephemeral ports exhausted by TIME_WAIT

# Cause: a new HTTP client per request, so no connection reuse. Every request
# opens and closes a socket, and each lingers in TIME_WAIT for 60 seconds.
# Fix: a single client with keep-alive and a connection pool. Not a kernel tunable.
```

## Notes

- "Cannot assign requested address" or "address already in use" under load is ephemeral-port exhaustion, and the cause is almost always a client created per request rather than reused. Tuning `tcp_tw_reuse` treats the symptom.
- Kubernetes `ndots:5` in the default `resolv.conf` means `api.example.com` generates several failed lookups before the correct one. On a DNS-heavy workload this is a measurable latency cost; `dnsConfig` with an explicit `ndots: 1` fixes it.
- MTU mismatches produce the strangest symptom in networking: small requests succeed and large ones hang forever. If TLS handshakes work but large POSTs stall, suspect path MTU.
