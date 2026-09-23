# Project 1 quality gate

**Scope result: runnable local PMO system and portable Power BI handoff delivered.** Power BI Desktop is explicitly outside the executed runtime boundary; its final assembly is documented rather than fabricated. No Project 2–5 implementation has been started.

| Required gate | Evidence / status |
|---|---|
| System actually runs | PASS — Python server and real local Chromium interaction executed |
| Synthetic portfolio internally consistent | PASS — relational validation and deterministic generation |
| Calculations and project-health logic | PASS — executed rule and boundary assertions |
| Financial calculations | PASS — transaction reconciliation and forecast variance tests |
| Milestones | PASS — actual lateness, due-today and open-date-floor tests |
| RAID | PASS — exposure, status, age, escalation and action calculations |
| Dependencies modelled | PASS — actual milestone/task FKs; 14 → 21 day UI scenario verified |
| Historical reporting | PASS — 12 periods, recovery/deterioration and no future-period leakage |
| Management reporting | PASS — report generated from the same engine and verified counts |
| Automated tests pass | PASS — exact counts and results in the test evidence files |
| README and diagrams match implementation | PASS — component/field review and link audit |
| Setup verified | PASS for Python launch in the build environment; native Windows and optional Docker not executed |
| Demo reproducible | PASS — scripted scenario interactions and reset verified |
| No credentials/secrets | PASS scoped pattern scan; no external credentials required |
| Synthetic disclosure | PASS — README, interface, examples, reports and portfolio copy |
| CV claims defensible | PASS — exactly three scope-based bullets, no fabricated savings or PBIX |
| Limitations documented | PASS — Power BI, Docker, deployment and model limitations explicit |
| GitHub readiness | PASS — source, data, docs, license, CI configuration and clean archive; no repository published |

## Final manual steps

- On the user's Windows PC: run the documented Python path and confirm the browser opens. Optional Docker has its own local build/start check.
- In Power BI Desktop: execute the supplied M/DAX, assemble seven pages and validate totals before saving the actual PBIX.
- If publishing: review the packaged synthetic files and README, create the repository and upload them. No publication was performed automatically.

Screenshots in this package are from the running **local management interface**, not Power BI. Passing this gate is not a production certification or an employer implementation claim.
