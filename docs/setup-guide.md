# Local setup and reproducible operation

## Recommended Windows path — Python

Python 3.12 or later is required. There are **no third-party runtime Python packages**, no paid API and no credentials. Extract the ZIP into a normal writable folder.

Open PowerShell in the folder containing `run.py`:

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe run.py
```

Open `http://localhost:8765` in your browser. The bundled processed files and baseline data are ready; no generation step is needed for first use. Keep the terminal open. Stop with Ctrl+C. The app uses port **8765**, leaving the existing n8n instance on **5678** untouched.

If `py` is not available, install Python from its official distribution and reopen PowerShell, or use `python` if that command already points to Python 3.12+. The `.venv` command is environment isolation; no activation or PowerShell execution-policy change is needed.

On macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python run.py
```

## Work with the interface

1. Start at Executive Portfolio with the latest period, 2026-09-21. Expected: 15 Active, 4 Green, 3 Amber and 8 Red; 2 Completed and 1 On Hold in the register.
2. Use Reporting period, Department and Health filters. Executive headline totals cover Active projects. Detail registers can include other lifecycle states and clearly label them.
3. Open Project Detail from a project link. It includes health drivers, milestones, finances, RAID, actions, dependency edges and history.
4. In Saved scenario controls choose a record type and record. Edit its forecast cost/date, risk values/status, issue status, action state or allocation hours. Save. The header changes to **SAVED SCENARIO** and dependent calculations refresh.
5. Thresholds are available under Project Health and Project Detail. Change them as a reporting assumption, save and compare outcomes. Reset all scenario edits restores both the original inputs and thresholds. The audit trail is retained.
6. Download Weekly report to get Markdown for the current period/filter. Export analytics writes all 12 scenario-aware periods to the repository's `output/` folder. Read `output/export-info.json` to confirm baseline/scenario mode.

Record edits affect one weekly snapshot. They do not silently rewrite all future periods, approvals or project baselines. Completed milestone forecasts are locked. If another tab saves first, refresh before retrying your edit. Reset is scoped to this demo's scenario overlay and is reversible by re-entering inputs; it never changes baseline files or the separate n8n project.

## Rebuild and test

Stop the server before changing canonical data. Run from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\build.py
.\.venv\Scripts\python.exe scripts\powerbi_assets.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\test_report.py
```

`build.py` recreates deterministic raw CSVs, typed JSON, processed analytical files, 12 historical JSON snapshots and weekly example reports. Manual changes to generated files will be overwritten. The generator is the source for intentional baseline changes. Rebuild does not erase scenario state; reset through the interface before comparing a new baseline.

Optional developer UI tests require Node.js and the dev packages in `package.json`. Start the Python server against disposable demo state, then in another terminal:

```powershell
npm ci
npm run test:ui
```

The DOM integration suite edits and resets synthetic scenario data, then exports analytics. Do not run it against a scenario you want to preserve. It is not a substitute for rendered-browser layout inspection.

## Optional Docker path

For users who already have Docker Desktop, an isolated Compose service is included:

```powershell
docker compose up -d --build
docker compose logs --tail=30
```

Open `http://localhost:8765`. It uses its own `pmo_state` and `pmo_output` volumes and does not reference `n8n_data`. Do not run the Python server and Docker service on port 8765 simultaneously. Exports inside Docker can be copied to the host:

```powershell
docker compose cp pmo:/app/output ./docker-output
```

Stop with `docker compose down`; retain volumes to keep scenario/audit data. Docker is an optional recipe, **not a container-runtime test result from this build**. The tested launch path is the local Python process.

## Power BI

Follow `powerbi/README.md`. The remaining Desktop work is to import the 14 typed tables, create 22 relationships, add the supplied DAX measures/theme, assemble seven pages and compare totals against the validation CSV. There is no fabricated PBIX. The local management interface is already implemented; it is independent of the Desktop assembly.

## Troubleshooting

- Address in use: stop the other local process or run `run.py --port 8766`, then use the matching URL.
- Cannot load baseline: ensure you extracted the complete folder; run `scripts/build.py` from it if files are missing.
- Invalid numeric/date/foreign-key errors: the input is rejected and prior state is preserved. Forecast cost must cover actual cost.
- Record locked: completed milestone actuals cannot be overwritten through the scenario editor.
- Table looks wide: use its horizontal scroll region; the page itself should remain usable on narrow screens.
- No scenario in Power BI: select Export analytics and change BaseFolder from `data/processed` to `output`; refresh in Desktop.
- Windows output file locked by Excel: close the file and retry export.

No connection to an employer system or external account is made. All dates are fixed synthetic reporting periods; today's calendar date does not alter the demo.
