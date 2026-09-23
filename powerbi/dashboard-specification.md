# Seven-page executive report specification

All pages use a light neutral canvas, dark teal headings and consistent semantic RAG colours. Target 16:9, readable labels, uncluttered tables and explicit scope subtitles. Use built-in Power BI visuals; no paid/custom visuals are required. The local management interface implements the same seven information views. This document specifies the remaining Desktop assembly, not an already-built PBIX.

| Page | Management question | Required visuals and fields | Interaction / acceptance |
|---|---|---|---|
| 1 Executive Portfolio | What needs intervention this week? | Cards: Active Projects, Critical Projects, Approved Budget, Forecast Variance. Stacked health bar; line of Critical Projects by DimPeriod; exception table with DimProject name/manager and FactProject RAG, variance and health dimensions | Single-period snapshot slicer; department slicer; trend ignores period slicer. Click/drill through a project. Latest 15 active; 4/3/8 RAG. |
| 2 Project Health | Which dimensions and departments drive concern? | Matrix: department × RAG count. Project register with lifecycle. Driver columns from schedule_rag, cost_rag, risk_rag, issues_rag, milestones_rag, dependencies_rag, actions_rag and reporting_rag | Use project selection to filter detail, rather than a fact-only RAG slicer that will not filter other fact tables. |
| 3 Schedule & Milestones | Which gates are late or threatened? | Cards: due in 14 days, overdue, critical overdue, average finish variance. FactMilestone table: baseline, forecast, actual, days_variance, status, criticality | Completed lateness remains visible but is not an open overdue item. At latest period 8 overdue, 4 critical in Active scope. |
| 4 RAID | What requires escalation, mitigation or action? | Risk matrix by probability/impact; risk register (exposure, owner, due, age, escalation); issue table; overdue action table | The scale is ordinal 1–25, not a percentage or money. Closed risks have no escalation. Registers include selected lifecycle rows; headline counts are Active only. |
| 5 Financial Performance | Which projects exceed funding tolerance? | Approved / actual / forecast cards; clustered bar by project; forecast variance table; forecast cost trend on project selection | Explain Actual − Planned separately from Forecast − Approved. Never sum financial snapshots over weeks. Latest variance €304,750. |
| 6 Dependencies | Where is cross-project exposure concentrated? | Edge table with upstream/receiving projects, milestone/task, availability, required date, exposure and criticality; matrix of upstream × downstream counts using the role dimensions | Built-in matrix/table is the portable relationship map. Local tool also shows linked edge cards. DEP01 shows 14 days exposure in baseline. No critical-path claim. |
| 7 Project Detail | What decision should the sponsor make? | Drill-through project card; lifecycle/RAG; plan vs forecast finish; financials; milestone register; risk/issues/actions; incoming/outgoing dependency evidence; weekly RAG, risk and forecast history | Keep reporting date and project filter. Validate P03/P04 supplier exposure; P07 recovery; P08 deterioration; P05 funding gap. |

## Layout guidance

Place snapshot date and synthetic-data disclosure on every page. Headline cards occupy the top row; evidence and decision tables dominate the lower half. Use colour plus words/icons, not colour alone. Show all amounts as simulated EUR with consistent rounding. Format blank actual dates as blank, not 1899 dates.

Use actual company-neutral labels and synthetic owners; never add employer branding or invented ROI. Capture screenshots only after Desktop refresh and validation. A finished screenshot does not prove refreshability: retain the actual PBIX and record the tested Desktop version in your own handoff notes.

## Desktop acceptance

Compare each reporting period against `validation-expected.csv`; check department totals, empty filter behaviour, same-day deadline boundaries, actual completion exclusions and project drill-through. Test BaseFolder replacement with a moved copy. Check measure totals with no selected date: guarded snapshot measures must be blank rather than summing 12 snapshots. Verify the trend visual shows one valid measure per weekly point.
