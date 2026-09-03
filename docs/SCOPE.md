# Scope

## What v1 Handles

- Single-table lookups and filters
- Multi-table joins across the schema
- Aggregations — counts, sums, averages, group-by
- Simple date-range filters
- Enum-based filtering (status codes, tier levels)
- ORDER BY and LIMIT
- NULL handling in aggregations

## What's Out of Scope for Now

- Multi-turn conversation or follow-up questions
- Any write operation. This stays read-only, permanently.
- Voice or other non-text input.
- Multi-database support (MySQL only)
- Query optimization suggestions
- Subqueries and CTEs
- Complex window functions

## Why These Boundaries

These keep the v1 focused on core accuracy: can Claude understand the schema and generate correct SELECT queries? Once that's solid, multi-turn conversation and optimization are natural extensions.
