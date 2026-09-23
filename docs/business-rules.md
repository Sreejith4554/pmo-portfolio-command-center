# KPI and health methodology

Authoritative functions: `src/pmo/engine.py`. Configuration: `config/health_rules.json`. An editor may save scenario-specific thresholds; source defaults remain unchanged.

## Overall RAG

Each dimension is Green, Amber or Red. Overall RAG is the **most severe** dimension. No random colours or opaque weighted average is used. Threshold comparisons below are inclusive (`>=`) unless stated otherwise.

| Dimension | Amber | Red |
|---|---|---|
| Schedule | Finish variance ≥5 days | Finish variance ≥14 days |
| Cost | Forecast overrun ≥5% | Forecast overrun ≥15% |
| Risk | Any open exposure ≥12 | Any open exposure ≥20 with mitigation Not started |
| Issues | Any open issue | Any unresolved Critical issue |
| Milestones | Any noncritical overdue milestone or open forecast variance ≥5 days | Any open Critical milestone overdue |
| Dependencies | Any direct incoming exposure >0 days | Critical dependency exposure ≥7 days |
| Actions | 1–2 overdue actions | ≥3 overdue actions |
| Reporting freshness | ≥10 days since last submitted update | No separate Red freshness rule |

An open critical risk with mitigation In progress still remains Amber; an unresolved Critical issue stays Red. A task delay appears in task evidence and contributes indirectly through the recorded project and milestone forecasts; task lateness alone is **not** an extra RAG rule. Resource overload is a portfolio warning, not an additional health dimension. These choices avoid counting the same delivery problem several times.

Completed and On Hold retain their calculated historical RAG for analysis but display their lifecycle badge. They are excluded from Active executive counts, financial totals and exception KPIs. The project register and evidence tables can still include them.

## Metric definitions

| KPI / field | Formula and management question |
|---|---|
| Active projects | Count of project-period rows with lifecycle Active: how much delivery work is live? |
| Healthy / At Risk / Critical | Active project counts with Green / Amber / Red: where should attention go? |
| Completion | Completed task count / all task count ×100. Unweighted progress, not earned value. |
| Finish variance | max(0, actual_finish or max(forecast_finish, reporting_date) − planned_finish), calendar days |
| Average schedule variance | Mean of Active project finish variances; no budget weighting |
| Milestone variance | (actual_date or max(forecast_date, reporting_date)) − baseline_date; negative actual variance means early completion |
| Overdue milestone | No actual date and baseline_date < reporting_date; due today is not overdue |
| Critical milestone overdue | Overdue milestone with Critical criticality |
| Milestones due | Open baseline date between reporting_date and reporting_date +14 days, inclusive |
| Approved budget | Sum of Active project approved budgets in the selected period |
| Actual spend | Cumulative actual transaction amounts through the reporting date, summed over Active projects |
| Planned cost | Period-specific planned cumulative spend, not earned value |
| Budget remaining | Approved budget − actual spend |
| Actual versus plan | Actual spend − planned cumulative spend; positive means more spent than planned |
| Forecast variance | Forecast cost at completion − approved budget; positive means expected overrun |
| Forecast variance % | Forecast variance / approved budget ×100. Portfolio percentage uses totals, never averages project percentages. |
| Projects over budget | Active projects with forecast variance >0, even below the Amber threshold |
| Risk exposure | Integer probability 1–5 × impact 1–5, giving ordinal exposure 1–25 |
| Critical risks | Open risks with exposure ≥configured red threshold, regardless of mitigation progress |
| Risk age | Reporting date − opened date for open risks; closed risk age displayed as zero (no close date captured) |
| Issue age | Resolution date or reporting date − opened date |
| Overdue actions | Open action with due_date < reporting_date |
| Dependency exposure | max(0, upstream availability + lag − downstream planned start), for unfinished downstream tasks |
| Overloaded resources | Allocated hours > available capacity; capacity never zero |

Money is synthetic whole EUR. Percentages are rounded to two decimals. Date differences use calendar days. Risk exposure is **not** a monetary amount and should not be presented as expected loss. A total risk score is useful for within-model trends only, not as a probability estimate.

## Dependency calculation

Each weekly edge references a real upstream milestone ID and downstream task ID. The validator enforces that the milestone belongs to the upstream project and the task to the receiving project. For unfinished milestones, effective availability is the later of forecast date and reporting date. For completed milestones it is the actual date. Lag is added before comparing with the downstream activity's planned start.

Example, latest baseline: `P03-M3` is available 2026-10-05 and `P04-T12` needs it 2026-09-21: **14 days of exposure**. Change the upstream forecast to 2026-10-12 in a saved scenario: the exposure becomes **21 days**. This does not rewrite the receiving project's finish forecast or compound downstream edges. Direct interface exposure and project-level planning remain separate judgments.

## Shared resources

Allocations are weekly project/resource facts. Workload sums across the **entire portfolio** before a department filter is applied. The interface shows resources used by the filtered projects with their full workload, avoiding a false spare-capacity signal. Default capacity is 40 hours per resource; the reporting assumption `resource_capacity_hours` proportionally scales nominal capacities. It is a sensitivity control, not an allocation optimiser or the future Resource Planning project.

## History and scenario semantics

There are 12 weekly periods from 2026-07-06 to 2026-09-21. Each is recomputed from its actual records, not from invented RAG history. UI history stops at the selected reporting date. A saved record edit affects one record in one period; it is a scenario, not a retroactive change to the baseline. Global scenario thresholds recalculate all periods under the same assumptions. Completed milestone forecasts are locked in the editor. Concurrent clients must submit the current revision; stale edits are rejected.

Reports compare the selected period with the previous available period, highlighting RAG, lifecycle and approved-budget changes. Recommended decisions are labeled rule-derived; no sponsor approval is fabricated. Report data, UI data and CSV exports use the same engine.
