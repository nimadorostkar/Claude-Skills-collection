---
name: cloud-architecture
description: Use when designing cloud infrastructure. Covers network topology, identity and least privilege, multi-AZ and multi-region trade-offs, managed versus self-hosted decisions, and designing for cost.
metadata:
  category: devops
  version: 1.0.0
  tags: [cloud, aws, architecture, networking, iam]
---

# Cloud Architecture

## Purpose

Design cloud infrastructure that is secure by default, appropriately available, and whose cost is a consequence of deliberate decisions rather than a monthly surprise.

## When to Use

- Designing infrastructure for a new system.
- Reviewing an existing architecture for security, availability, or cost.
- Deciding between managed services and self-hosting.
- Planning a multi-region or disaster-recovery strategy.

## Capabilities

- Network topology: VPCs, subnets, gateways, private connectivity.
- Identity: least-privilege roles, federation, and eliminating long-lived keys.
- Availability design: multi-AZ, multi-region, RTO and RPO.
- Managed-versus-self-hosted evaluation.
- Cost modeling as a design input.

## Inputs

- Workload characteristics: stateful or stateless, traffic shape, data gravity.
- Availability requirements, expressed as RTO and RPO, not adjectives.
- Compliance and data-residency constraints.
- Budget.

## Outputs

- A network and identity design with least privilege by default.
- An availability posture matched to the stated RTO/RPO.
- A cost model with the drivers identified.

## Workflow

1. **Start with the data** — Where it lives, who may see it, and how much it costs to move. Data gravity determines more of the architecture than compute does.
2. **Design the network for isolation** — Private subnets for compute and data; public exposure only through a load balancer or gateway. Nothing with a database on it should have a public IP.
3. **Grant least privilege** — Roles scoped to actions and resources. Wildcards in IAM policies are how a compromised container becomes a compromised account.
4. **Match availability to requirement** — Multi-AZ is cheap and should be the default for anything production. Multi-region is expensive, complex, and justified only by an RTO that genuinely demands it.
5. **Prefer managed services** — Unless you have a specific reason and the staff to operate the alternative. Self-hosting a database to save money usually costs more in engineer time within a year.
6. **Model the cost** — Egress, cross-AZ traffic, NAT gateways, and idle capacity are the surprises. Estimate them before building, not after the invoice.

## Best Practices

- Least privilege is not an aspiration; it is a default. Start with no permissions and add what fails.
- Long-lived access keys are the most common cloud breach vector. Use roles, instance profiles, and OIDC federation — and set an organizational policy that forbids creating static keys.
- Cross-AZ data transfer costs money. A chatty service split across three AZs pays for every hop, and the bill is invisible until it is large.
- NAT gateways are billed per hour *and* per gigabyte. A workload pulling large images through NAT is a line item people find months later. Use VPC endpoints for AWS services.
- Multi-region active-active is one of the most expensive decisions available. It requires solving data replication, conflict resolution, and routing — for an availability gain most products do not need.
- Tag everything, from the first resource. Retrofitting tags for cost attribution across an existing account is a project.

## Examples

**Least-privilege role: scoped to the action, the resource, and the condition:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOwnTenantObjectsOnly",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::app-uploads/${aws:PrincipalTag/tenant_id}/*"
    },
    {
      "Sid": "WriteOwnTenantObjectsOnly",
      "Effect": "Allow",
      "Action": ["s3:PutObject"],
      "Resource": "arn:aws:s3:::app-uploads/${aws:PrincipalTag/tenant_id}/*",
      "Condition": {
        "StringEquals": { "s3:x-amz-server-side-encryption": "aws:kms" }
      }
    }
  ]
}
```

Compare with `"Action": "s3:*", "Resource": "*"`, which is what most policies start as and far too many stay as.

**Cost drivers, identified at design time:**

```text
Monthly estimate (eu-west-1, steady state):

  ECS Fargate    6 tasks x 1vCPU/2GB, 24/7          ~$180
  RDS Postgres   db.r6g.large, Multi-AZ             ~$430
  ALB            1 + ~2 TB processed                 ~$40
  NAT Gateway    2 AZs x $0.045/hr + 800 GB egress   ~$105   <-- surprise #1
  S3             400 GB + requests                    ~$12
  CloudWatch     Logs ingest 300 GB                   ~$150   <-- surprise #2
  Data transfer  cross-AZ chatter, ~1.5 TB            ~$15
                                                    -------
                                                     ~$932

Actions taken at design time:
  - S3 and ECR reached via VPC endpoints, not NAT: NAT egress drops to ~100 GB (-$65).
  - Log sampling for debug-level in production, 30-day retention: (-$95).
  Revised: ~$772/month, with the two largest surprises removed before they appeared.
```

## Notes

- CloudWatch Logs ingestion is billed per gigabyte and is routinely the second- or third-largest line on a bill for a service that logs verbosely. Sample debug logs; keep errors.
- A single NAT gateway is a single point of failure; one per AZ is the resilient configuration and doubles the hourly cost. VPC endpoints avoid both problems for AWS-service traffic.
- "We might need multi-region later" is not a reason to build it now. It is a reason to keep state in one place and avoid decisions that make a future migration impossible.
