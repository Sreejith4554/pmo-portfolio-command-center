# Security and privacy

All entities, owners, financial amounts and delivery events are synthetic. No passwords, API keys, email addresses or external service credentials are required. The baseline and screenshots do not identify any real employer or customer.

## Local boundary

`run.py` binds to 127.0.0.1 by default. The optional Docker port is also published to host loopback. This is a local, single-user demo, not a publicly hosted service. Do not expose it through a public reverse proxy without authentication, TLS and authorization.

The API rejects unexpected Host values, requires a random per-process header token for writes and rejects cross-origin browser POSTs. These measures reduce unintended cross-site/local requests and DNS-rebinding exposure; they are not user authentication. A local process able to read the token can also edit synthetic scenario data. No secret data should be stored in this demo.

Only named tables and fields are editable. Record and rule validation occurs before committing changes. SQLite transactions and revision checks prevent stale concurrent updates. The server returns generic unexpected-error messages; local logs hold tracebacks without deliberately logging request bodies. Frontend text is escaped before HTML insertion.

## Persistence

`state/scenarios.sqlite` holds scenario edits, revision number and audit history. Baseline files are not modified by the interface. Reset clears the scenario overlay and rules, preserving the audit. No encryption at rest, tamper-evident audit, backup scheduler or retention policy is implemented. Use OS disk protections and add appropriate controls before adapting to real organisational data.

Generated exports are in `output/`; they are ignored by Git because later user scenarios could contain unwanted content. `.env`, database files, logs, virtual environments and dependencies are also excluded. The packaged screenshots and examples use only bundled synthetic data. Review staged files before publication and enable repository secret protection where available.

## External effects

The application does not send email, post to Slack, contact AI services or publish anything to GitHub. Export writes local files; report download returns local Markdown. No browser/CDN requests are required during normal use. Development test dependencies are optional and installed through the standard npm registry.

## Before production

Add identity/access controls, network/TLS protection, governance approvals, secure connectors, schema/version migrations, retention, backups/restore tests, monitoring, supported dependency policies and load testing. Assess CSV formula injection and other untrusted-source risks if accepting arbitrary text from live systems. None of those production assurances is implied by this synthetic portfolio build.
