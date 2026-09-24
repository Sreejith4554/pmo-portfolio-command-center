# Power BI Implementation

This folder contains the Power BI implementation of the **PMO Portfolio Command Center**.

The report has been assembled and validated in Power BI Desktop using the analytical datasets, Power Query definitions, DAX measures, relationship metadata, theme and validation outputs maintained in this repository.

> **Independent portfolio project:** All project, financial, resource, RAID and delivery data is synthetic. No employer, client or real organisation is represented.

## Report overview

The completed Power BI report contains seven management-facing pages:

1. **Executive Portfolio** — portfolio health, financial position, trends and management exceptions.
2. **Project Health** — project-level RAG status, governance drivers and department-level visibility.
3. **Schedule & Milestones** — schedule variance, milestone performance and overdue delivery gates.
4. **RAID & Actions** — risks, issues and action ownership.
5. **Financial Performance** — approved budget, actual spend, forecast spend and variance.
6. **Dependencies** — cross-project dependency exposure and shared-resource visibility.
7. **Project Detail** — selected-project delivery, financial, schedule, milestone, RAID and historical evidence.

A separate **QA - Validation** page was used during development to reconcile Power BI outputs against the repository's expected baseline.

## Report preview

### Executive Portfolio

![Executive Portfolio](../screenshots/01-executive-portfolio.png)

### Project Health

![Project Health](../screenshots/02-project-health.png)

### Schedule & Milestones

![Schedule and Milestones](../screenshots/03-schedule-milestones.png)

### RAID & Actions

![RAID and Actions](../screenshots/04-raid-actions.png)

### Financial Performance

![Financial Performance](../screenshots/05-financial-performance.png)

### Dependencies

![Dependencies](../screenshots/06-dependencies.png)

### Project Detail

![Project Detail](../screenshots/07-project-detail.png)

## Analytical model

The Power BI implementation uses a dimensional model rather than a single flattened reporting table.

The model includes:

- **14 typed analytical data queries**
- a configurable `BaseFolder` parameter
- **22 active relationships**
- many-to-one relationship design
- single-direction filtering
- dedicated project, reporting-period, resource and upstream-project dimensions
- DAX measures for portfolio-level and project-level management reporting

The reporting model includes:

- `DimPeriod`
- `DimProject`
- `DimResource`
- `DimUpstreamProject`
- `FactAction`
- `FactAllocation`
- `FactCost`
- `FactDependency`
- `FactIssue`
- `FactMilestone`
- `FactProject`
- `FactResource`
- `FactRisk`
- `FactTask`

`DimProject` represents the receiving/downstream project role for dependencies, while `DimUpstreamProject` provides the separate upstream-project role.

Fact tables are not connected directly to one another.

## Power Query

The `queries/` directory contains the portable Power Query definitions used to construct the analytical model.

`BaseFolder.pq` provides the source-folder parameter.

The remaining queries:

- read the processed CSV datasets;
- promote headers;
- normalize empty values;
- assign explicit data types;
- prepare the dimensional and fact tables used by the report.

The source path can be changed through `BaseFolder` when the repository is moved to another machine.

## Relationships

The model uses **22 active, single-direction, many-to-one relationships**.

The relationship design is documented in:

- `relationships.csv`
- the accompanying relationship metadata

The model deliberately avoids unnecessary bidirectional filtering and direct fact-to-fact relationships.

This keeps filter propagation explicit and reduces the risk of ambiguous filtering or portfolio double-counting.

## DAX measures

The report uses a dedicated measures table for portfolio calculations.

Measures include:

- Active Projects
- Healthy Projects
- At Risk Projects
- Critical Projects
- Approved Budget
- Actual Spend
- Forecast Spend
- Forecast Variance
- Forecast Variance Percent
- Average Completion Percent
- Average Schedule Variance
- Open Risks
- Critical Risks
- Open Issues
- Critical Issues
- Overdue Actions
- Overdue Milestones
- Critical Milestones Overdue
- Milestones Due
- Dependency Exposure
- Portfolio Overloaded Resources
- Projects Forecast Over Budget
- Previous Period Red Projects
- Red Project Change
- Selected Reporting Date
- Project Count

Snapshot measures are designed around a single selected reporting period so that project and budget snapshots are not incorrectly summed across multiple weekly periods.

Historical visuals use reporting-period context to display portfolio movement over time.

## Latest-period validation

The Power BI report was checked against `validation-expected.csv` for the latest reporting period:

**2026-09-21**

| Measure | Expected / validated result |
|---|---:|
| Active projects | 15 |
| Green | 4 |
| Amber | 3 |
| Red | 8 |
| Approved budget | €6,775,000 |
| Actual spend | €5,888,268 |
| Forecast spend | €7,079,750 |
| Forecast variance | €304,750 |
| Forecast variance % | 4.50% |
| Overdue milestones | 8 |
| Critical overdue milestones | 4 |
| Dependency exposure | 2 |
| Overloaded shared resources | 4 |

The displayed Power BI outputs matched these expected latest-period values during Desktop validation.

## Reporting-period design

`DimPeriod` contains the project's **12 weekly reporting periods**.

The reporting-period dimension is intentionally not treated as a contiguous daily calendar.

Snapshot pages use a selected reporting date, while historical trend visuals retain the weekly reporting history required to show changes over time.

The validated latest reporting date is:

```text
2026-09-21
```

## Project Detail behaviour

Project Detail uses a **single-project selector** to investigate an individual project's delivery evidence.

The validated example uses **Beacon Finance Platform**, demonstrating:

- completion progress;
- forecast variance;
- schedule variance;
- open risks;
- open issues;
- lifecycle and overall RAG status;
- milestone performance;
- outstanding actions;
- historical project-health movement.

A dedicated drill-through configuration is not required for this portfolio implementation.

## Theme and visual design

`theme.json` provides the report's visual foundation.

The report uses a restrained PMO-oriented visual system with:

- neutral report canvas;
- dark teal headings;
- management KPI cards;
- semantic RAG reporting;
- structured registers and matrices;
- limited decorative elements;
- consistent page hierarchy.

The report uses standard Power BI visuals rather than requiring custom marketplace visuals.

## Reproducing the model

To reconstruct the analytical model in Power BI Desktop:

1. Clone or download the repository.
2. Open Power BI Desktop.
3. Create the `BaseFolder` parameter using `queries/BaseFolder.pq`.
4. Point it to the repository's `data/processed` directory.
5. Create the remaining analytical queries from the `.pq` files in `queries/`.
6. Disable load for `BaseFolder`.
7. Close & Apply.
8. Create the **22 relationships** documented in `relationships.csv`.
9. Keep the documented relationships active and single-direction.
10. Create the supplied DAX measures from `measures.dax`.
11. Import `theme.json`.
12. Build or inspect the seven management pages using `dashboard-specification.md`.
13. Select `2026-09-21` when validating the latest-period snapshot.
14. Compare the resulting KPIs with `validation-expected.csv`.

When moving the repository, update `BaseFolder` before refreshing the model.

## Portfolio data disclosure

All information in this report is synthetic.

This includes:

- project names;
- project owners;
- sponsors;
- departments;
- budgets;
- costs;
- forecasts;
- risks;
- issues;
- milestones;
- actions;
- dependencies;
- resource allocations;
- reporting history.

The scenarios were intentionally designed to demonstrate PMO governance and portfolio-analysis behaviours.

They should not be interpreted as employer, customer or organisational results.

## Scope and limitations

The Power BI implementation is designed as a portfolio demonstration rather than an enterprise production reporting deployment.

It does not claim:

- live enterprise-system connectivity;
- production authentication;
- row-level security;
- automated enterprise refresh;
- critical-path scheduling;
- earned-value management;
- automatic resource optimisation;
- predictive project outcomes;
- automated recovery decisions.

The report provides structured evidence for management analysis; it does not replace project or portfolio management judgment.

## Supporting assets

This folder contains the reproducible Power BI handoff assets, including:

```text
queries/                    Power Query definitions
measures.dax                DAX measure definitions
relationships.csv           Relationship specification
theme.json                  Power BI theme
dashboard-specification.md  Report/page specification
validation-expected.csv      Expected baseline KPI values
```

The repository also contains the processed analytical datasets used by the report.

## Power BI Desktop deliverable

A completed Power BI Desktop report has been produced and successfully reopened after saving.

Where the `.pbix` is distributed with the repository, it represents the portfolio report built from the synthetic analytical model documented above.

The portable source assets remain available independently so the analytical design can be inspected or reconstructed without relying solely on the binary Power BI file.

---

**PMO Portfolio Command Center · Independent portfolio project · Entirely synthetic data**
**Independent portfolio project · Entirely synthetic data**
