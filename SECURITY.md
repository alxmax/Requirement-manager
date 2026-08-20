# Security policy

## Reporting a vulnerability

Use GitHub's private reporting: **Security → Advisories → Report a vulnerability** on
<https://github.com/alxmax/Requirement-manager>. That opens a draft advisory only the
maintainer can see.

Please do not open a public issue for a vulnerability first.

This is a solo-maintained project, so triage is best-effort rather than an SLA. Expect an
acknowledgement within a week; if a report is valid it is fixed in the next release and
credited in `CHANGELOG.md` unless you ask otherwise.

## What is supported

Only the latest release. There are no backports — the fix ships in the next `vX.Y.Z`, and
the `check@v2` alias is force-moved onto it. **`check@v1` is frozen** at plugin v2.1.0
content and receives nothing, including security fixes; pins on it should move to `@v2`.

## What is in scope

The parts of this project that run somewhere you did not write:

- **`check/action.yml` and `check/engine_staleness.py`** — the published GitHub Action,
  which executes inside a consumer's CI.
- **`plugin/scripts/reqmap.py`** — the engine, which reads every file in a repo it is
  pointed at and writes generated artifacts. Anything that lets repository *content* (a
  file name, a tag, a requirement body) escape into code execution, or into the generated
  HTML as script, is in scope. The `_map.html` viewer inlines a repo's `_map.json` into a
  `<script>` block, which is the sharpest edge here and has had dedicated hardening
  (`</script>` sequences, U+2028/U+2029, lone surrogates).
- **`plugin/hooks/pre-commit`** — shipped into consumer repos and run on their commits.

A useful framing for a report: *what can a repository whose contents I do not control make
this tool do to the machine running it?*

## What is out of scope

- Findings that require write access to the repository being scanned — someone who can edit
  the code being gated can already run code in CI.
- Resource exhaustion from deliberately huge or pathological inputs (a 1 GB source file, a
  million-file tree). The engine is not hardened against a hostile local operator.
- A missed drift, a false warning, or any other correctness bug in the gate. Those are
  real, and they belong in a normal issue.
- Vulnerabilities in GitHub Actions, Python, or the runner image itself. Report those
  upstream; if this repo pins an affected version, do open an issue.

## Notes for consumers

The gate needs no secrets and no write scope. Keep the caller workflow at
`permissions: contents: read` — the action never writes to your repo, and granting it more
only widens what a compromised dependency could reach. `actions/setup-python` inside the
action is pinned to a full commit SHA, so a re-pointed upstream tag cannot execute in your
run.
