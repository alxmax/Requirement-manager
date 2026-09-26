# 0054 — Invalid input cannot produce a passing verdict

Status: Accepted. Date: 2026-09-26. Amends [0026](0026-gate-rule-registry-and-config-file.md)
(item 5, the configuration file, and RM016's unconditional warning severity).

## Context

Dropping duplicate IDs or unreadable requirements silently changes the corpus
being checked. A configuration entry that is reported on stderr and skipped can
also weaken intended policy without the verdict saying so. A missing initial
baseline and a corrupt existing baseline are different states.

The first draft of this record made a bad `_config.json` fatal for every command.
That turns a one-key typo into a red build for every consumer on upgrade, the
`mcp` server included, which this repository's rule treats as a breaking change
for an `@v8` pin.

## Decision

- Requirement loading keeps diagnostics for duplicate IDs, non-string IDs and
  unreadable files. `gate` reports them as `INPUT:requirements` errors in both
  output formats, and `sync` does not advance its locks over them. The first
  duplicate stays available to read-only queries.
- Configuration stays fail-open, as 0026 decided: a malformed file or an invalid
  entry is reported on stderr and skipped, and no command stops on it. The bare
  `gate` verdict now carries each one as an `INPUT:config` warning, so text and
  JSON both show it, and `gate --strict` promotes it to an error. Retired keys stay
  silent.
- A corrupt requirement lock (RM016) warns normally and fails `--strict`; an
  absent lock stays valid at first use.

## Consequences

A passing strict verdict now requires usable input; a passing bare verdict still
tolerates a bad configuration entry, but no longer hides it. This validates input
integrity, not the semantic correctness of requirements or their implementations.
Recovery is explicit: fix the source or configuration, or restore a corrupt lock;
run `sync` on purpose to establish a replacement baseline.

## Revisit when

A consumer asks for a bad configuration entry to fail the bare gate, or a new
configuration type or baseline format is introduced.
