# 0054 — Invalid input cannot produce a passing verdict

Status: Accepted. Date: 2026-09-25.

## Context

Dropping duplicate IDs or unreadable requirements silently changes the corpus
being checked. Ignoring invalid configuration can also weaken intended policy.
A missing initial baseline and a corrupt existing baseline are different states.

## Decision

The CLI rejects malformed configuration and invalid active settings before
command dispatch. Library configuration helpers keep their compatible fallback
behavior and expose an optional diagnostic collector. Retired keys remain ignored.
Requirement loading retains diagnostics for duplicate IDs, non-string IDs and
unreadable files. Gate reports these as errors in both output formats and does
not advance its locks. The first duplicate remains available for read-only queries.
A corrupt requirement lock warns normally and fails strict mode; an absent lock
remains valid at first use. This amends the earlier CLI fail-open configuration
policy and the unconditional warning severity for RM016.

## Consequences

A passing verdict now requires usable input. This validates input integrity,
not semantic correctness of requirements or their implementations. Recovery is
explicit: fix the source/configuration, or restore a corrupt lock before checking;
use sync intentionally to establish a replacement baseline.

## Revisit when

Additional configuration types or baseline formats are introduced.
