# Test strategy and actual evidence

## What was executed

Python tests run the real validation/calculation functions, a temporary SQLite scenario database and actual local HTTP servers. DOM integration tests execute the real frontend script in jsdom against the actual API. Browser integration tests launch real local Chromium, navigate all seven views, save a milestone scenario, verify the rendered dependency change, reset, change filters and check mobile overflow. Screenshots are actual browser captures.

| Test layer | Evidence | Boundary |
|---|---|---|
| Data, rules, state and HTTP | `test-results.md` / `.json` | Tests run against synthetic data and local server |
| DOM/API controls | `ui-test-results.json` | Executed JavaScript interactions; not a visual test |
| Rendered browser | `browser-test-results.json` | Local Chromium interactions and real screenshots |
| Analytical schema / repository | `package-audit.json` | Unique dimension keys, FK coverage, column references, links and focused secret patterns |
| Power BI | `powerbi/validation-expected.csv` | Expected totals supplied; M/DAX engine and Desktop not executed |
| Docker / Windows | Setup guide | Optional Docker and native Windows execution remain local checks |

## Core expected results

| Scenario | Expected |
|---|---|
| Latest portfolio | 18 total, 15 Active, 2 Completed, 1 On Hold |
| Latest Active health | 4 Green, 3 Amber, 8 Red |
| Finances | Budget €6,775,000; actual €5,888,268; forecast €7,079,750; variance €304,750 |
| Critical milestone count | 4 active critical overdue gates |
| Dependency baseline | DEP01 = P03-M3 → P04-T12, 14 days exposure |
| Dependency scenario | Change P03-M3 forecast to 2026-10-12; exposure becomes 21 days |
| Risk threshold | Integer 1–5 probability/impact; exposure product; closed risks do not escalate |
| Due-today actions | Not overdue |
| Completed late gate | P04-M1 = 3 days late; not open overdue |
| Recovery / deterioration | P07 Red → Green; P08 Amber → Red |
| Shared-resource workload | Four overloaded resources at latest baseline; department filter does not hide other allocations |
| Invalid input | Rejected; no saved revision increment |
| Stale concurrent edit | Rejected until refresh |
| Reset | Baseline restored; audit retained |
| Historical selection | No later reporting periods appear in the UI's selected-period history |

## Reproduce

Run `python scripts/test_report.py`. To test the UI, run `python run.py` in one terminal and `npm ci`, then `npm run test:ui` in another. Use disposable scenario state: the UI suites intentionally save and reset synthetic data. `PMO_STATE_DIR` can point the server at a separate writable test directory.

For browser tests, install the Playwright Chromium binary using `npx playwright install chromium`, then `npm run test:browser`. Set `PMO_TEST_URL` if using another port. An already installed compatible Chromium can be selected through `PMO_BROWSER_EXECUTABLE`. Test dependencies are optional; normal users need only Python and their browser.

The build environment used a local Chromium executable supplied from a reputable npm-distributed headless Chromium package after the standard browser download was unavailable. This is documented tooling, not an application dependency. No user credentials or external production system were exercised.

## Remaining Power BI acceptance

In Desktop, import the data and supplied transformations, establish relationships and create measures. Check single-period totals, department filtering, null dates, source-folder portability, trend context, drill-through and the resource-filter caveat. Save a real PBIX only after those checks. Do not label screenshots from the local application as Power BI.

## Testing limits

No load/soak tests, penetration test, multi-tenant authorization review, Windows GUI automation or production recovery exercise was performed. Automated tests establish the documented synthetic behaviour, not proof that arbitrary organisational inputs are trustworthy. The CI workflow is provided but was not run on GitHub during this build.
