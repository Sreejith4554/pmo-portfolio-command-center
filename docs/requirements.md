# Requirements and acceptance criteria

**Scope: Project 1 only.** This system demonstrates portfolio governance and management reporting. The existing n8n delivery automation project was inspected and remains unchanged. Planning/earned value, resource optimisation, process simulation and project recovery simulation are future, separately authorised projects; they are not implemented here.

## Business requirements

| ID | Management need | Acceptance evidence |
|---|---|---|
| B01 | Know which active projects need intervention and why | RAG and named health drivers reconcile with milestones, costs, RAID and dependencies |
| B02 | Make the weekly portfolio review repeatable | Report, interface and analytical exports use the same calculation functions |
| B03 | Identify cross-project exposure | Upstream milestone forecast change alters the receiving task's exposure |
| B04 | Separate financial facts from forecasts | Transactions reconcile to cumulative actual cost; forecast variance uses approved budget |
| B05 | Track deterioration and recovery | Twelve dated periods; River recovers, Beacon deteriorates |
| B06 | Make input changes safely during a demonstration | Saved scenario overlay, revision checks, audit history and reset |
| B07 | Support executive Power BI reporting | Typed datasets, relationships, queries, measures and seven-page specifications |

## Functional requirements

F01: 18 projects across seven fictional departments. F02: period, department and RAG filters. F03: seven usable management views. F04: project drill-through and evidence. F05: documented configurable RAG rules. F06: milestone lateness including actual completion. F07: risk exposure/age, issues and action tracking. F08: genuine dependency joins. F09: shared resource overload visibility. F10: baseline and scenario history. F11: deterministic Markdown management report. F12: CSV analytics export. F13: controlled synthetic-record updates, rules, reset and audit. F14: data-quality rejection and user-visible errors.

## Non-functional requirements

N01: Python 3.12+ standard-library runtime, with no paid API or external CDN dependency. N02: reproducible generators and source-controlled defaults. N03: SQLite used only for scenario/audit state. N04: local-only service by default, bounded writes and same-origin protection. N05: no credentials or personal data. N06: keyboard-operable semantic controls, responsive layout and text labels as well as colours. N07: tests for boundaries, financial reconciliation, foreign keys, propagation, persistence and API behaviour. N08: synthetic disclosure visible in the interface and reports. N09: no false claims about PBIX, browser visual testing, employer deployment or realised savings.

## Scope decisions

Completed and On Hold are lifecycle states, separate from health. Active-only executive KPIs avoid describing closed work as a current delivery crisis. Registers can show all lifecycles in the chosen filter. Cost values are simulated whole euros; risk scores are ordinal, not expected monetary values. Dependencies quantify direct exposure and do not claim to calculate a critical path or propagate an automatic schedule change. Capacity reporting shows overload but does not allocate or optimise resources.
