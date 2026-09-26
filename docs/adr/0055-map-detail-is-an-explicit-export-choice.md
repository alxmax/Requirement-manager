# 0055 — Map detail is an explicit export choice

Status: Accepted. Date: 2026-09-25.

## Context

The map repeated detailed source content in diagrams and embedded JSON whitespace.
Translation caches also made every offline export carry every available locale.

## Decision

Keep the full profile as the compatible default. Add a compact profile with a
Markdown overview and minified JSON. Always minify the offline viewer payload.
MAP_LOCALES independently selects cached translations; source contracts, cases,
nodes and links are retained. This repository opts into compact with no caches.
Compare JSON content semantically so formatting is not a freshness failure.
The existing single offline viewer policy (ADR-0034) remains in force.

## Consequences

Markdown becomes a navigation entry point in compact mode. Complete source content
stays in JSON and HTML; translations remain on disk and can be re-enabled.
Minimal initialization is additive and skips optional scaffolding without deleting
existing files. It does not change the map profile or the normal init default.

## Revisit when

Measured viewer payload or rendering time still obstructs a real consumer task.
