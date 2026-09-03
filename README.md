# TalkToData: English to SQL

Type a question in plain English and get back a SQL query plus the answer. No SQL knowledge required.

## What This Is

TalkToData converts natural language questions into executable MySQL queries. It safely executes them, returns results as a table, and shows you the generated SQL so you understand what happened.

**Example:**
- Question: "Which carrier had the lowest revenue per flight?"
- Generated SQL: Multi-table JOIN with revenue calculation, CASE WHEN filtering, GROUP BY
- Result: 6-row table with carrier codes and revenue metrics

## How It Works

1. Schema Introspection — Queries INFORMATION_SCHEMA at runtime (works with any MySQL database)
2. Dynamic Prompt — Builds context with live schema + enum meanings (no hardcoding)
3. SQL Generation — Claude API generates SELECT queries with extended thinking
4. Safety Validation — Blocks writes (INSERT/UPDATE/DELETE), prevents injection, validates before execution
5. Self-Correction — On DB errors, captures error message, feeds back to Claude, retries once
6. Result Comparison — Executes query, compares results (order-insensitive)

## Accuracy & Performance

- Baseline: 58.3% (7/12 test cases)
- After Optimization: 75.0% (9/12) — +16.7 percentage points
- Key Improvement: Emphasized exact enum codes in prompt (prevented "Delayed" vs "DL" confusion)
- Test Categories: Lookup (100%), Filter (50%→100%), Join (50%), Aggregation (0%→50%), Date Range (50%→100%)

See docs/accuracy_report.txt for full breakdown.

## Tech Stack

- Claude API (claude-sonnet-5) — SQL generation with extended thinking
- MySQL 8.0 — Database (via Docker for reproducibility)
- Python — anthropic, mysql-connector-python, pandas, pytest, streamlit, pyyaml
- Streamlit — Interactive web UI
- Docker Compose — Zero-friction setup

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Anthropic API key

### Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create .env with your API key:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. Start MySQL:
```bash
docker-compose up -d
sleep 15
docker-compose ps
```

4. Verify connection:
```bash
python3 test_connection.py
```

Should output flight status counts from the database.

### Run the App

```bash
streamlit run app.py
```

Opens at http://localhost:8501

### Run Tests

```bash
touch src/__init__.py tests/__init__.py
PYTHONPATH=. python -m pytest tests/ -v
```

## Architecture

### Directory Structure

```
src/
  config.py                 # Centralized settings (DB, API, model)
  schema_introspection.py   # Live INFORMATION_SCHEMA discovery
  sql_generator.py          # NL→SQL with self-correction loop
  safety.py                 # Query validation (write-blocking, injection prevention)
  executor.py               # Execute queries, compare result-sets

tests/
  test_eval.py              # Evaluation harness (12 gold test cases)
  test_safety.py            # Safety validation (9 test cases)
  test_generator.py         # SQL generator tests
  test_executor.py          # Executor tests
  gold_sql.yaml             # Hand-curated questions + expected results

docs/
  accuracy_report.txt       # Before/after accuracy metrics
  SCOPE.md                  # v1 boundaries

Root files:
  schema_hints.yaml         # Enum meanings & column semantics
  docker-compose.yml        # MySQL 8.0 container
  .env.example              # Credentials template
```

## Features

- Dynamic Schema — Live discovery via INFORMATION_SCHEMA (works with any MySQL DB)
- Safety-First — Blocks INSERT/UPDATE/DELETE, prevents injection, validates all queries
- Self-Correction — Captures DB errors, retries with error context
- Result Comparison — Order-insensitive equality (semantic correctness)
- Measured Accuracy — 12 gold test cases, tracked before/after optimization
- Production Ready — Docker + environment config, no secrets in code
- Extended Thinking — Handles Claude's reasoning blocks correctly

## Testing & Evaluation

### Gold Test Cases (12 total)

**Lookup (4):** COUNT(*), SELECT with ORDER BY, listing carriers/passengers/bookings

**Filter (2):** WHERE with status codes, flights by carrier

**Join (2):** Multi-table joins (flights+bookings+passengers), complex logic

**Aggregation (2):** GROUP BY with SUM/AVG, revenue per flight calculation

**Date Range (2):** YEAR/MONTH filtering, MAX datetime

### Running Evaluation

```bash
PYTHONPATH=. python -m pytest tests/test_eval.py -v
```

### Safety Test Coverage

9 test cases for safety layer:
- Simple SELECT
- Joins
- Aggregations
- INSERT blocked
- UPDATE blocked
- DELETE blocked
- DROP blocked
- ALTER blocked
- SQL injection (semicolon chaining) blocked

## Example Queries

"How many flights are there?"
```sql
SELECT COUNT(*) as cnt FROM flights
```

"Which carrier has the most flights?"
```sql
SELECT c.carrier_name, COUNT(f.flight_id) as flight_count 
FROM carriers c 
LEFT JOIN flights f ON c.carrier_cd = f.carrier_cd 
GROUP BY c.carrier_cd, c.carrier_name 
ORDER BY flight_count DESC LIMIT 1
```

"What is the average delay per carrier?"
```sql
SELECT c.carrier_name, AVG(f.delay_min) as avg_delay 
FROM carriers c 
LEFT JOIN flights f ON c.carrier_cd = f.carrier_cd 
GROUP BY c.carrier_cd, c.carrier_name 
ORDER BY avg_delay DESC
```

"How much revenue did each loyalty tier generate?"
```sql
SELECT p.loyalty_tier, SUM(b.fare_amt) as revenue 
FROM passengers p 
LEFT JOIN bookings b ON p.pax_id = b.pax_id 
WHERE b.status_cd = 'CF' 
GROUP BY p.loyalty_tier 
ORDER BY revenue DESC
```

## Future Work

- Multi-Database Support: Postgres, SQLite connectors (currently MySQL-only)
- Embedding-Based Retrieval: Few-shot examples + schema subset selection for large databases
- Multi-Turn Conversation: Follow-up questions on previous results
- Query Optimization: Suggest indexes, rewrite inefficient queries

## Troubleshooting

**Port 3306 in use?**
```bash
docker-compose down
docker volume prune -f
docker-compose up -d
```

Or change port in docker-compose.yml (3306→3307) and update .env

**MySQL connection denied?**
- Verify .env has correct credentials
- Check Docker container is healthy: `docker-compose ps`
- Wait 30 seconds after startup (MySQL initializes slowly)

**Python import errors?**
```bash
touch src/__init__.py tests/__init__.py
PYTHONPATH=. python -m pytest tests/ -v
```

## License

MIT

## Author

Built as a portfolio project to demonstrate NL→SQL generation, LLM integration, prompt engineering, and production-grade safety/testing practices.
