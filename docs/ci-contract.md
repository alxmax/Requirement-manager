# CI contract — this repository

Public repo. Minutes are not the 2000-minute private budget. The job of CI
here is to prove the engine and the published Action, not to run a product stack.

| # | Rule | Status |
|---|---|---|
| E1 | Engine tests on Python 3.9 and 3.12, Ubuntu only. Drop 3.13×Windows from the required matrix once `release` does not `needs` every cell. | open |
| E2 | One `gate --full` on `plugin/requirements/`, in `gate-and-tests`. Do not run it inside the matrix. | already in `ci.yml` |
| E3 | Dogfood: `uses: alxmax/requirement-manager/check@v8` on the README pin. Workflow: `.github/workflows/dogfood.yml`. Red means the README is wrong. | this PR |
| E4 | `scripts/check_versions.py` and the CORE budget stay in the short `gate-and-tests` job. Do not copy them into every matrix cell. | already in `ci.yml` |
| E5 | Release / `@v8` move only on push to `main` or a tag. Do not also run deploy/release on `pull_request` for the same SHA. | open (release job already `if: push && main`) |

`pull_request` + `workflow_dispatch` for checks. `push` to `main` only for Pages and release.

Not in scope: Docker, frontend, API, debounce, fail-on-drift on `@v8`.
