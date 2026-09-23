# Data model and validation

## Raw relational source

| Table | Grain / key | Main relationships |
|---|---|---|
| departments | department_id | Referenced by projects |
| people | person_id | Project managers, sponsors and RAID owners |
| projects | project_id | Department, manager and sponsor; stable baseline dates and scenario story |
| resources | resource_id | Nominal weekly capacity |
| periods | reporting_date | Twelve weekly dates and ordered period_index |
| statuses | project_id + reporting_date | Lifecycle, phase, forecast/actual finish, last report date |
| budgets | project_id + reporting_date | Approved, planned and forecast cost; simulated EUR |
| costs | cost_id | Project and transaction_date; incremental actual amount |
| milestones | milestone_id + reporting_date | Project, baseline, forecast, actual, criticality |
| tasks | task_id + reporting_date | Project, planned start, due and actual completion |
| risks | risk_id + reporting_date | Project, owner, probability/impact, mitigation and status |
| issues | issue_id + reporting_date | Project, owner, severity, opened/due/resolution dates |
| actions | action_id + reporting_date | Project, owner, due and completion state |
| assumptions | assumption_id + reporting_date | Project, sponsor owner, review date and state |
| dependencies | dependency_id + reporting_date | Upstream project/milestone → receiving project/task |
| allocations | allocation_id + reporting_date | Project, resource and weekly hours |

Counts across all periods: **6,629 source rows** in 16 tables. At each reporting period: 18 project statuses, 18 budgets, 72 milestones, 216 tasks, 54 risks, 36 issues, 54 actions, 18 assumptions, seven dependency edges and 36 allocation records. The source also includes 216 incremental cost transactions across the full history. Counts of source rows do not imply that every record is open or active.

The typed `data/raw/portfolio.json` bundle stores these tables separately and is the runtime source. CSV copies support inspection and portability. They are generated outputs, not a second competing source of truth.

## Analytical model

| Dimension / fact | Grain |
|---|---|
| DimProject | One row per project, with denormalized department/manager/sponsor attributes |
| DimPeriod | One row per weekly reporting date |
| DimResource | One row per resource |
| DimUpstreamProject | One row per upstream-role project |
| FactProject | Project × period; 216 rows |
| FactMilestone / FactTask / FactRisk / FactIssue / FactAction | Entity × period |
| FactDependency | Dependency edge × period; receiving-project and upstream-role keys |
| FactAllocation | Project/resource allocation × period |
| FactResource | Resource × period; full-portfolio load and capacity |
| FactCost | Incremental cost transaction |

`PortfolioKPI.csv` is a verification output, not an extra fact to join into the model. Joining it to detailed facts would double-count totals. Assumptions remain in the operational source/UI; they are not a separate supplied Power BI fact.

`powerbi/table-schemas.json` documents every exported column, type and nullability. `relationships.csv` is the exact one-to-many relationship map. Export checks verify one-side uniqueness and all relationship key coverage.

## Data-quality enforcement

Validation rejects duplicate entity-period keys, unknown project/person/resource references, missing budget/status coverage, nonexistent periods, invalid dates, future actual dates, finish-before-start records, negative/nonfinite amounts, zero budgets, forecasts below actual spend, probability/impact outside integer 1–5, missing tasks, completion-state mismatches, invalid issue resolution and mismatched dependency ownership.

Actual cost is derived from transactions, avoiding a separately editable actual-total field. A scenario forecast must still cover actual spending. Baseline milestones remain consistent across history; budget movement is a real changed approval value in the synthetic records. Health is recomputed, never randomly generated.

Limitations: there is no daily calendar, holiday treatment, multi-currency conversion, formal earned-value baseline, graph-cycle scheduling engine, risk monetary loss model or transaction approval workflow. Source changes are validated in a batch; an external live ingestion connector is not implemented.
