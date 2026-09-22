---
id: HELLO-GREET-001
status: confirmed
layer: feature
owner: you
---

# Greet a user by name

## Description
> The one behaviour this demo has, so the one drift it shows is easy to see.

Every bullet below is binding.
- `greet(name)` returns `Hello, <name>!`, with spaces around `name` removed first.

## Cases
CASE-1 — a name is greeted
  Given  the name "Ada"
  When   `greet("Ada")` runs
  Then   it returns "Hello, Ada!"
