# TalkToData

Ask your database a question in plain English and get back the SQL query and the answer. No SQL knowledge required on your end.

## What this is

TalkToData takes a question like "which customers spent the most last quarter?" and turns it into a working SQL query against a real, multi-table database. It checks that query for safety before running it, executes it, and hands back a results table plus a plain-English summary.

The point isn't just "call an LLM and print what it says." The interesting part is everything around that: making sure the generated SQL is actually safe to run, handling joins and aggregations correctly, and being honest about where it fails.

## How it works

A question comes in as plain text. Claude generates SQL for it using the database schema as context. A safety layer checks the query before anything executes — no writes, no exceptions. SQLite runs the (read-only) query, and the results come back as a table with a short explanation.

## Tech stack

- Claude API for query generation
- SQLite for the database
- Python (pandas, python-dotenv) for the pipeline
- Streamlit for the interface

## Status

Early stage — currently setting up the database and schema documentation. Check `docs/SCOPE.md` for what v1 will and won't handle.

Roadmap:
- Load the dataset into SQLite and document the schema
- Build and test the core text-to-SQL prompt
- Add the safety and validation layer
- Build the Streamlit interface
- Test against a set of sample questions and track accuracy
- Write up the results

Once the core pipeline is solid, I'm planning to add a few ML pieces on top: embedding-based retrieval for the schema/examples, a classifier that flags harder questions, and clustering to find patterns in what the model gets wrong.

## Setup

Coming soon — this section gets filled in once the pipeline actually runs.
