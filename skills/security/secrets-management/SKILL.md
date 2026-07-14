---
name: secrets-management
description: Use when handling credentials, API keys, and certificates. Covers secret storage, rotation, injection into applications, detection of leaked secrets, and what to do when one is exposed.
metadata:
  category: security
  version: 1.0.0
  tags: [secrets, credentials, rotation, vault, leak]
---

# Secrets Management

## Purpose

Keep credentials out of code, out of logs, and out of git history — and be able to rotate them quickly when, inevitably, one leaks.

## When to Use

- Setting up secret storage for an application.
- A secret has been committed or exposed.
- Implementing rotation.
- Auditing a repository or a running system for exposed credentials.

## Capabilities

- Secret storage: cloud secret managers, Vault, sealed secrets.
- Injection: environment, mounted files, SDK-based retrieval.
- Rotation, including zero-downtime rotation of database credentials.
- Leak detection in code, history, logs, and error reports.
- Incident response for an exposed secret.

## Inputs

- The secrets an application needs, and their blast radius if leaked.
- The runtime and how it can receive them.
- The rotation capability of each upstream provider.

## Outputs

- No secrets in the repository, the image, or the logs.
- Secrets injected at runtime from a managed store.
- A rotation procedure that has been tested.

## Workflow

1. **Eliminate static credentials first** — Prefer workload identity: IAM roles, OIDC federation, managed identities. A secret that does not exist cannot leak. This is the single most effective change available.
2. **Store what remains in a secret manager** — Never in code, never in a config file in the repository, never in a container image layer.
3. **Inject at runtime** — Mounted file or environment variable, fetched from the manager at start. The application never contains the value.
4. **Redact in logs** — Structured logging with a redaction filter on known secret field names, and never logging the full request body of an auth endpoint.
5. **Scan continuously** — A pre-commit hook and a CI scan on the full history. Detection after the fact is far better than not detecting it.
6. **Rotate on a schedule and on exposure** — And test the rotation before you need it in an emergency.

## Best Practices

- A secret committed to git is compromised the moment it is pushed, regardless of whether the repository is private, whether it was force-pushed away, or whether anyone noticed. Rotate it. Deleting the commit is not a remediation.
- Environment variables are visible in `/proc`, in crash dumps, in some error reporters, and to any process running as the same user. A mounted file with restricted permissions is stronger.
- Rotation must be zero-downtime: support two valid credentials simultaneously (issue the new one, deploy, revoke the old one). A rotation that requires an outage will not be done.
- Never pass a secret as a command-line argument. It is visible in `ps` to every user on the host.
- Do not build a secret into a container image, even in a "private" registry. Image layers are extractable with `docker history` and are cached in many places.
- Short-lived, dynamically generated credentials (Vault's database secrets engine, IAM database authentication) make rotation continuous and leak impact minimal.

## Examples

**Workload identity: the secret that does not exist:**

```yaml
# Instead of an AWS access key in a Kubernetes Secret, the pod assumes a role.
# There is no long-lived credential anywhere to leak.
apiVersion: v1
kind: ServiceAccount
metadata:
  name: orders-api
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/orders-api
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      serviceAccountName: orders-api      # the SDK now obtains temporary credentials
      containers:
        - name: api
          env:
            - name: DATABASE_URL          # what genuinely must be a secret is
              valueFrom:                  # mounted from a manager, not baked in
                secretKeyRef: { name: orders-db, key: url }
```

**Responding to an exposed secret — in the right order:**

```text
1. ROTATE. Immediately, before anything else. The old credential is dead.
   Do not investigate first; the investigation can happen while the new
   credential is deploying.

2. REVOKE the old credential at the provider. Rotation without revocation
   means the leaked value still works.

3. AUDIT the access logs for use of the old credential between the leak and
   the revocation. Assume it was used until you have evidence otherwise.

4. REMOVE it from the code and the history if practical (git-filter-repo,
   or ask the host to purge). This is cleanup, not remediation.

5. PREVENT the recurrence: add the pattern to the pre-commit scanner, and
   ask why a human had access to a raw credential at all.
```

**Scanning the history, not just the tree:**

```bash
gitleaks detect --source . --log-opts="--all"     # every commit on every branch
trufflehog git file://. --only-verified           # verifies the key is live
```

## Notes

- `trufflehog --only-verified` actually attempts to authenticate with the discovered credential, which distinguishes a live key requiring immediate rotation from an expired one that is merely embarrassing.
- Sealed Secrets and SOPS allow encrypted secrets to live in git safely, which is a reasonable model for GitOps. The encryption key still lives in a manager.
- The most common source of a leaked secret is not the repository — it is a log line, an error report sent to a third party, or a screenshot in a support ticket. Redact at the logger.
