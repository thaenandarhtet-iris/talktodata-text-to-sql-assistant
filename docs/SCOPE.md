# Scope

## What v1 handles
- Single-table lookups and filters
- Multi-table joins across the sample database
- Aggregations — counts, sums, averages, group-by
- Simple date-range filters

## What's out of scope for now
- Multi-turn conversation or follow-up questions
- Any write operation. This stays read-only, permanently.
- Voice or other non-text input. Worth revisiting once the core pipeline works, not before.

Keeping this list visible is mostly a discipline thing — it's easy to let "just one more feature" creep in before the basics are solid.
