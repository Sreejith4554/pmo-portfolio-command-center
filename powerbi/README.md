# Power BI handoff — portable assets, no PBIX claim

Power BI is the preferred executive analytics layer. Power BI Desktop is not available in the build environment: **no `.pbix`, `.pbit` or runnable Power BI report is claimed or supplied**. This folder contains genuine CSV-ready assets: explicit typed M queries, DAX measure definitions, a theme, relationship metadata and seven-page build specifications. Calculated CSV values are executed and tested in Python; M, DAX and visual configuration require Desktop validation.

## Exact Desktop steps

1. Extract the project to a permanent Windows folder. Baseline files already exist in `data/processed`. To use saved scenario results, run the local tool and choose **Export analytics**; files are then in `output/`.
2. Open Power BI Desktop → Blank report → Transform data → New Source → Blank Query. Rename it `BaseFolder`. Open Advanced Editor and paste `queries/BaseFolder.pq`, replacing the placeholder with the full folder path, for example `C:/Users/YourName/Documents/pmo-portfolio-command-center/data/processed`. Forward slashes avoid escaping issues.
3. Create one blank query for each of the other **14** `.pq` files. Name each query exactly as its filename without `.pq`; paste its content into Advanced Editor. The queries read UTF-8 CSV, promote headers, replace empty fields with null and assign explicit types. Set `BaseFolder` to `output` for scenario analytics when desired. Disable load for the `BaseFolder` parameter.
4. Close & Apply. In Model view remove auto-detected relationships that conflict with `relationships.csv`. Create its **22** relationships exactly: dimension on the one side, fact on the many side, **Single** filter direction, Active. Each listed one-side key is unique and validated in the build checks.
5. Do **not** connect fact tables directly. `DimProject` is the receiving project role for dependencies. `DimUpstreamProject` is a separate upstream role. `FactResource` connects only to period/resource dimensions; do not invent a project relationship that would double-count capacity.
6. `DimPeriod` has 12 reporting dates, not a contiguous daily calendar. Sort period labels by period_index. Do not mark it as a daily date table or use daily time-intelligence functions. Supplied prior-period DAX uses period_index.
7. Create the measures in `measures.dax` individually using New measure. Use `FactProject` as their home table or move them to your own Measures table. Do not paste the whole multi-measure file as a single expression.
8. Import `theme.json` under View → Themes → Browse for themes. Build the pages in `dashboard-specification.md`. For RAG colours, configure explicit field/value conditional formatting: Green `#13785C`, Amber `#D0A259`, Red `#B43A3D`; theme palette order alone does not establish semantic RAG colours.
9. Add a **single-select** `DimPeriod[reporting_date]` slicer on snapshot pages and select `2026-09-21`. For the weekly trend line, disable interaction from that slicer so all 12 periods are visible; each chart point still supplies one period. Prefer page-level lifecycle labels over a blanket lifecycle filter because it would hide closeouts in detail views.
10. Add Project Detail drill-through on `DimProject[project_id]` with Keep all filters enabled. Verify the selected reporting period is retained. Use dimensions in slicers and rows rather than trying to cross-filter sibling facts through a fact-level RAG slicer.
11. Validate against `validation-expected.csv`. Latest baseline: 15 Active, 4 Green, 3 Amber, 8 Red; budget €6,775,000; actual €5,888,268; forecast €7,079,750; forecast variance €304,750. Confirm no double-counting when changing periods.
12. Save your actual report as `PMO-Portfolio-Command-Center.pbix`. Only then describe it as a working Power BI dashboard. Test refresh after moving folders by updating BaseFolder.

## Filter caveats

Snapshot measures deliberately return blank if multiple periods are selected; summing snapshots would count the same project/budget repeatedly. Table visuals from milestone, risk, issue and action facts show all lifecycles in the selected filter, matching the local interface; headline measures use Active-only aggregates from FactProject. A fact-level lifecycle or RAG filter does not automatically propagate to sibling facts under single-direction relationships. Use DimProject selections/drill-through for consistent detail filtering, or create carefully tested measure filters if you extend the model.

The supplied resource measure is portfolio-wide. The local app narrows visible resources to those used by the filtered projects but retains full workload; reproducing that exact presentation in Power BI requires a measure/visual filter over allocation membership. Do not enable bidirectional filtering merely to force it.

Percentages in CSV are on a 0–100 scale. Supplied DAX percentage measures divide appropriately and should be formatted as Percentage. Format raw `forecast_variance_pct` and `percentage_complete` as decimal numbers with a `%` suffix, or create divided-by-100 measures; otherwise 25 becomes 2500%.

## Official reference basis

- [Microsoft: star-schema guidance](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [Microsoft: Csv.Document](https://learn.microsoft.com/en-us/powerquery-m/csv-document)
- [Microsoft: Table.TransformColumnTypes](https://learn.microsoft.com/en-us/powerquery-m/table-transformcolumntypes)
- [Microsoft: CALCULATE](https://learn.microsoft.com/en-us/dax/calculate-function-dax)

These references informed the structure; they do not validate this particular report's DAX/M execution. That remains a Desktop step.
