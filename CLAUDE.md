# CLAUDE.md

Project rules for any AI assistant working in this repository. This file is committed on purpose: reviewers may read it.

## Project

Patient Cohort Explorer: a Python API plus a React screen that loads fake patient data (4 CSV files in `data/`) and finds groups of patients matching rules defined as JSON. Take-home task, three parts:

1. Backend (most weight): idempotent import with a reject report, a generic JSON cohort-rule engine, 4 API endpoints, summary under 2 s on the full data, tests focused on cohort logic and data edge cases.
2. Frontend: cohort form, results table (server-side paging, sorting, search), summary panel, patient history page.
3. Code review: `REVIEW.md` for the PR on branch `feature/cohort-csv-export`. Review only, never fix that code.

`review/` is the existing service used for Part 3 only. It is not part of our solution, it is not run, and we never edit it. Our own solution lives in new top-level folders.

## Task constraints (from the task document)

- About one working day of effort (6-8 hours). Do not spend more. If time runs out, stop and write down what we would do next.
- All data is fake, about 50,000 patients and 600,000 rows, a simplified OMOP-like shape: `patients`, `conditions`, `medications`, `lab_results`. It came from several source systems: **do not assume it is clean**. Finding the problems, deciding how to handle each, and listing them in the README is part of the task.
- Unclear rule wording: choose one meaning, write it in the README, say why. The reviewers look at these choices closely.
- The first cohort: adults aged 40 to 65 at first type 2 diabetes diagnosis, who started metformin within 90 days after that diagnosis, and whose most recent HbA1c is above 7.0%. Type 2 diabetes = ICD-10 `E11` and sub-codes (e.g. `E11.9`), or SNOMED `44054006`. Drug names are free text as typed in the source system.
- The rule format must express this cohort **and** a similar one with a different disease, drug, lab test or time window. Do not hard-code the diabetes cohort.
- `POST /cohorts` (save and validate), `GET /cohorts/{id}/patients` (server-side paging, sorting, search), `GET /cohorts/{id}/summary` (count, counts by sex, counts by 10-year age band; under 2 s on the full data on a normal laptop), `GET /patients/{id}` (diagnoses, drugs, labs in date order).
- Frontend: simple, works, easy to use. Sorting on column headers, one search box above the table, server-side paging.
- Optional, only after everything else is solid: `docker compose up`, CSV export of a cohort, compare two cohorts.
- AI tools are allowed, here and in the follow-up interview. What counts is that the developer understands and owns every line, and can explain and change it live.

## Stack

Python 3.11+, FastAPI, React with TypeScript, **PostgreSQL** (decided: real date types, strong date arithmetic and `EXPLAIN`, closer to the backend role). Postgres runs in a single Docker container for development; the API and the frontend run locally (fast reload, easy debugging). The query layer (raw SQL vs SQLAlchemy Core) and the project layout are **open**: they are decided after we have looked at the data, and each decision is written down with its reason. Full `docker compose up` for the whole app is optional and comes last, only if the core is solid.

Planned libraries (exact versions are checked at install time):

- Backend: FastAPI, pydantic v2, a Postgres driver (psycopg 3 unless the query-layer decision says otherwise), pytest.
- Tooling: `uv` for the Python environment and dependencies, `ruff` for lint and format.
- Tests run against a real PostgreSQL (a separate test database), never SQLite: the generated SQL uses Postgres date arithmetic and window functions, so another engine would prove nothing.
- Frontend: Vite, TypeScript, React, TanStack Query, TanStack Table (manual server-side pagination and sorting), react-hook-form with zod, shadcn/ui. Use few components (table, input, button, select, card); do not spend time on theming.

## Engineering rules

- Clean, working, tested code beats feature count. Stop and write down what is left rather than rush.
- Abstract only for a real reason (a second implementation, a real swap point). Premature abstraction is as bad as none. Simple beats clever.
- The cohort engine must stay generic. Nothing about diabetes, metformin or HbA1c may be hard-coded in engine code; it lives only in example cohort definitions and tests.
- SQL: always parameterised values. Field, operator and table names that come from a cohort definition are mapped through an allowlist, never interpolated.
- Every data problem we find gets (1) a decision, (2) a test, (3) a README entry. Rejected import rows keep a reason code.
- Import must be idempotent: running it twice gives the same database.
- Tests are written with the code they cover, in the same commit. Edge cases from the data come before happy paths.
- Versions and APIs of libraries are checked in the installed package or live docs, not from memory.
- No comments unless they explain a non-obvious why. Docstrings are fine.
- Code, identifiers, comments, commit messages and docs are English only.
- Secrets live in a git-ignored `.env`. Never commit a database file or generated data.

## Git rules

- Commit as we work: small, one logical change each, tests included. The history is read by the reviewers.
- Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`).
- Work on `main`, linear history. Amend or squash and force-push (`--force-with-lease`) only when the developer asks, to keep the history clean; never squash the whole history into one commit.
- Never commit to, merge or rebase `feature/cohort-csv-export`.
- Never commit unless the developer asks for it.

## Deliverables that are easy to forget

`README.md` must contain: run it in 5 steps or fewer; data problems found and how each was handled; choices on unclear rules and why; AI usage (tools and parts, at least one place the AI was wrong or weak and what was done, decisions made against the AI); what we would do with one more day. `REVIEW.md` for Part 3.
