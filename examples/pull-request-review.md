# Reviewing a pull request

**Skills loaded:** `code-review`, then `secure-coding`
**Outcome:** One blocking finding that no automated scanner reports

---

## The request

> Review this PR: it adds an endpoint to fetch an invoice by ID.

```python
@router.get("/invoices/{invoice_id}")
@requires_auth
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    return invoice
```

The tests pass. Linting is clean. Bandit and CodeQL report nothing.

## Without the skills

A typical review of this code notes that it looks fine: it authenticates, it handles the not-found case, it returns a 404 rather than a 500. Perhaps a suggestion to add a response model.

That review misses a reportable data breach.

## What the skills changed

`code-review` enforces an order — correctness, then security, then performance — and one specific check under security:

> **Audit every authorization check.** For each endpoint taking an identifier: is there a check that the caller may access *that specific object*?

`secure-coding` names the vulnerability class explicitly:

> Broken object-level authorization (BOLA/IDOR) is consistently the top API vulnerability. Every endpoint that takes an ID must check that the caller may access *that* object. A route guard is not enough.

## The review

### Blocking — `api/invoices.py:3` — Broken object-level authorization

`@requires_auth` verifies that the caller is *logged in*. It does not verify that the invoice belongs to them.

The identifier is a sequential integer. Any authenticated user — including a free-tier account created thirty seconds ago — can read every invoice in the system:

```bash
for i in $(seq 1 100000); do
  curl -H "Authorization: Bearer $TOKEN" https://api.example.com/invoices/$i
done
```

Invoices contain customer names, billing addresses, line items, and amounts. This is a reportable personal-data breach under GDPR, and it is discoverable by anyone who changes a number in a URL.

**Fix:**

```python
@router.get("/invoices/{invoice_id}", response_model=InvoiceRead)
async def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    invoice = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == user.tenant_id)
        .first()
    )
    if not invoice:
        # 404, not 403. A 403 confirms the invoice exists, which is itself a leak.
        raise HTTPException(404, "Invoice not found")
    return invoice
```

**Also — defence in depth:** migrate invoice IDs from sequential integers to ULIDs. Enumeration then becomes infeasible even if an authorization check is missed again somewhere else. Sequential integers additionally leak your invoice volume to anyone who creates two invoices a month apart.

**Verification:** a test that authenticates as tenant A, requests an invoice belonging to tenant B, and asserts 404. The absence of that test is why this reached review.

### Should fix — no `response_model`

The endpoint returns the ORM object directly, so every column on `Invoice` is serialized — including `internal_notes` and `cost_basis_cents`, which are not customer-facing. Adding a field to the model in six months will silently expose it through this endpoint.

### What works

The 404-on-missing behavior is correct, and the not-found path is handled before the response is constructed. Keep both.

---

## What the skills contributed

| The finding | The rule that fired |
| --- | --- |
| The vulnerability at all | `code-review`: *For each endpoint taking an identifier: is there a check that the caller may access that specific object?* |
| 404 rather than 403 | `secure-coding`: *Same response for "does not exist" and "not yours": do not leak existence.* |
| The ULID recommendation | `secure-coding`: *Sequential integer IDs leak business information and are enumerable.* |
| The `response_model` finding | `code-review`: *Anything crossing a trust boundary must be encoded on the way out.* |
| The missing test | `code-review`: *Check the tests, not just the code. A missing authorization test usually means a missing authorization check.* |

Bandit and CodeQL both passed this file. Static analysis finds known-bad patterns; it does not find *absent* authorization, because there is no pattern to match. That is the specific gap the review skill exists to close.
