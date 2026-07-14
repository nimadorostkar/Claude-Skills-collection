---
name: aws-cost-optimization
description: Use when reducing cloud spend. Covers finding the actual cost drivers, right-sizing, commitment discounts, storage lifecycle, the hidden costs of data transfer and logging, and avoiding false savings.
metadata:
  category: devops
  version: 1.0.0
  tags: [cost, finops, aws, optimization, budgets]
---

# AWS Cost Optimization

## Purpose

Reduce cloud spend by finding where the money actually goes, which is rarely where people assume. Most cost work targets compute; most surprises are in data transfer, logging, and idle resources.

## When to Use

- The bill grew and nobody can explain why.
- Before committing to reserved capacity or savings plans.
- Reviewing an architecture for cost as a design property.
- Setting up cost attribution and budgets.

## Capabilities

- Cost analysis: Cost Explorer, Cost and Usage Report, tag-based attribution.
- Right-sizing compute and storage against real utilization.
- Commitment discounts: reserved instances and savings plans.
- Storage lifecycle and tiering.
- Identifying the hidden drivers: NAT, cross-AZ, egress, CloudWatch, idle resources.

## Inputs

- The Cost and Usage Report, or Cost Explorer grouped by service and by tag.
- Utilization metrics for the top spend items.
- Growth expectations — commitments are a bet on future usage.

## Outputs

- A ranked list of cost drivers with the savings available from each.
- Changes made, with the measured before and after.
- Budgets and anomaly alerts so the next surprise is caught early.

## Workflow

1. **Find the actual drivers** — Group the bill by service, then by tag, then by usage type. Do not act on intuition; the top three line items are frequently not what anyone guessed.
2. **Delete the waste first** — Unattached EBS volumes, idle load balancers, old snapshots, unused Elastic IPs, forgotten dev environments. This is free money and requires no trade-off.
3. **Right-size against real utilization** — An instance running at 8% CPU for three months is oversized. Use Compute Optimizer, and check the memory metric too.
4. **Fix the hidden drivers** — NAT gateway data processing, cross-AZ transfer, CloudWatch Logs ingestion, and S3 request costs. These are invisible in a per-service summary and often account for 20% of the bill.
5. **Then commit** — Savings plans and reserved instances give 30-70% off, but only after right-sizing. Committing to your current oversized footprint locks in the waste for three years.
6. **Attribute and alert** — Tags on everything, a budget per team, and anomaly detection so the next 40% jump is caught in a day, not a month.

## Best Practices

- Commit last, not first. A three-year reservation on an instance you should have downsized is the most expensive kind of optimization.
- CloudWatch Logs ingestion at roughly $0.50/GB makes verbose debug logging in production a real line item. Sample it, and set retention — logs default to being kept forever.
- Cross-AZ traffic is charged in both directions. A chatty service mesh spread across three AZs pays a transfer fee for every internal call.
- S3 Intelligent-Tiering is nearly always correct for data with unknown access patterns. The monitoring fee is trivial next to the savings on cold objects.
- Graviton (ARM) instances are typically 20-40% cheaper for the same performance. For most managed services and interpreted languages, migrating is a configuration change.
- Non-production environments running 24/7 are a pure waste. Scheduling them to stop outside working hours cuts their cost by roughly 70%.

## Examples

**Finding the driver, not the assumption:**

```bash
# The bill jumped 38%. Group by usage type, not by service — the service view
# said "EC2-Other", which explains nothing.
aws ce get-cost-and-usage \
  --time-period Start=2026-05-01,End=2026-07-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=USAGE_TYPE \
  --query 'ResultsByTime[].Groups[?Metrics.UnblendedCost.Amount>`500`]' \
  --output table
```

```text
Result:
  EU-NatGateway-Bytes     $3,180  (was $410)     <- the entire increase
  EUC1-EBS:VolumeUsage      $890
  EU-DataTransfer-Out       $640

Cause: a new service pulls 4 GB container images from a public registry on
every task start, through the NAT gateway, and it scales to 200 tasks.

Fix: mirror the image into ECR and add an ECR VPC endpoint. NAT bytes for
that workload go to zero. Saving: ~$2,900/month, for two hours of work.
```

**Right-sizing before committing:**

```text
Current:  30 x m6i.2xlarge, average CPU 11%, average memory 34%
Step 1:   right-size to m7g.large (Graviton)   -> $8,400/mo becomes $2,600/mo
Step 2:   1-year Compute Savings Plan on the new footprint (-31%) -> $1,790/mo

Committing before right-sizing would have locked in $8,400/mo at a discount
to $5,800/mo — and made the right-sizing financially pointless for a year.
```

## Notes

- The single most common large surprise on an AWS bill is NAT gateway data processing, because it is billed per gigabyte and appears under the opaque "EC2-Other" usage category.
- Savings Plans are more flexible than Reserved Instances (they apply across instance families and regions) and are the right default unless you have a very stable, specific footprint.
- Cost anomaly detection is free and catches the class of problem that a monthly review catches four weeks too late. Turn it on before you need it.
