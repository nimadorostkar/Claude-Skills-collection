# Changelog

All notable changes to this repository are recorded here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A skill's guidance is an interface. Changing what a skill tells an agent to do is a breaking change for anyone whose workflow depends on it, and it is versioned as one.

## [Unreleased]

Nothing yet.

## [1.0.0] — 2026-07-14

First public release. 137 skills across 17 categories, each following a single template and a single voice.

### Added

**Languages** (12) — Python, TypeScript, Go, Rust, Java/Kotlin, C#/.NET, C++, PHP, Ruby, Swift, SQL, Shell.

**Development** (13) — Code review, debugging, refactoring, bug-fix protocol, design patterns, system design, architecture decisions, legacy modernization, git workflow, repository exploration, domain modeling, simple design, CLI development.

**Backend** (11) — API design, GraphQL, microservices, event-driven architecture, realtime and WebSockets, caching, background jobs, FastAPI, Django, Spring Boot, NestJS.

**Frontend** (9) — React, Next.js, Vue, Angular, frontend architecture, design systems, accessibility, web performance, visual QA.

**Mobile** (4) — iOS, React Native, Flutter, mobile release.

**DevOps and Cloud** (13) — Kubernetes, Terraform, containers, CI/CD, observability, site reliability, incident response, chaos engineering, cloud architecture, AWS CDK, AWS serverless, AWS cost optimization, network troubleshooting.

**Data** (6) — PostgreSQL, database performance, data modeling, pandas, Spark, data quality.

**Security** (5) — Secure coding, security review, threat modeling, secrets management, supply chain.

**Testing** (6) — Test strategy, TDD, Playwright end-to-end, web application testing, performance testing, QA review.

**AI and LLM** (12) — Prompt engineering, context engineering, RAG, LLM evaluation, agent design, structured output, LLM integration, MCP servers, fine-tuning, ML pipelines, model selection, LLM cost optimization.

**Agent Tooling** (8) — Skill authoring, skill review, agent instructions, hooks, subagents, plugin development, agent memory, slash commands.

**Finance** (12) — Position sizing, risk management, technical analysis, market breadth, market regime, stock screening, backtesting, options strategy, portfolio review, earnings analysis, trade journal, quantitative analysis.

**Documents** (6) — Word documents, spreadsheets, presentations, PDF, diagrams, document conversion.

**Design** (5) — Visual design, brand guidelines, theming, generative art, UI review.

**Writing** (5) — Technical documentation, changelog, internal communications, long-form content, editing.

**Productivity** (5) — Deep research, fact-checking, meeting notes, file organization, web data extraction.

**Business** (5) — Competitive analysis, product analysis, user research, lead research, resume.

### Infrastructure

- A single nine-section template, enforced by `scripts/validate.py` in CI.
- Category indexes and a full catalog, generated from the skills themselves so they cannot drift.
- Authoring and standards documentation.
- Three worked examples showing skills in use end to end.
