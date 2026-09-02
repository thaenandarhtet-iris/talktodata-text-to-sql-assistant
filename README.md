# TalkToData

Type a question in plain English and get back a SQL query plus the answer. No SQL knowledge required.

## What this is

TalkToData takes a question like "which customers spent the most last quarter?" and turns it into a working SQL query against a real, multi-table MySQL database. It checks the query for safety before running it, executes it, and returns a results table along with a short plain-English summary.

The interesting part isn't just calling an LLM and printing what it says. It's everything around that: making sure the generated SQL is actually safe to run, handling joins and aggregations correctly, and being upfront about where the model gets things wrong.

## How it works

A question comes in as plain text. Claude generates SQL for it, using the database schema as context. A safety layer checks the query before anything runs, no writes are ever allowed. MySQL executes the read-only query, and the results come back as a table with a short explanation.

## Tech stack

- Claude API for query generation
- MySQL for the database, currently running Chinook, a sample dataset with customers, invoices, and tracks
- Python (pandas, python-dotenv, mysql-connector-python) for the pipeline
- Streamlit for the interface

## Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Anthropic API key

### Quick Start

1. Clone the repo and install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your ANTHROPIC_API_KEY:
   ```bash
   cp .env.example .env
   ```

3. Start MySQL with Docker:
   ```bash
   docker compose up -d
   ```

4. Wait for MySQL to be ready (~5 seconds). Check status:
   ```bash
   docker compose ps
   ```

5. Verify the connection:
   ```bash
   python test_connection.py
   ```

You should see output: `[(0, '5'), (1, '12'), ...]` (status_cd counts).

### Stopping

```bash
docker compose down
```

The data persists in Docker volumes and reloads on next `up`.

## Status

Early stage. Right now I'm setting up the database and documenting the schema. Check `docs/SCOPE.md` for what v1 will and won't handle.

Roadmap:
- Load the dataset into MySQL and document the schema
- Build and test the core text-to-SQL prompt
- Add the safety and validation layer
- Build the Streamlit interface
- Test against a set of sample questions and track accuracy
- Write up the results

## AI/ML integration (tentative)

These are just the directions I'm exploring:

- Embedding-based retrieval, so the app only pulls in the relevant tables and past examples for a given question instead of dumping the whole schema into every prompt
- A small classifier trained on my own test questions to flag which ones are likely to need a join or an aggregation
- Clustering on the questions the model gets wrong, to see if the failures follow a pattern instead of just listing them one by one
