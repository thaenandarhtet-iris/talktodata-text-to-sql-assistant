rm docs/accuracy_report.py
cat > docs/accuracy_report.txt << 'EOF'
ACCURACY REPORT: Measurably More Accurate NL→SQL

BASELINE (Before Optimizations)
================================
Measured on 12 hand-authored gold questions across 5 categories.

Overall Accuracy: [To be measured]

By Category:
- Lookup: TBD
- Filter: TBD
- Join: TBD
- Aggregation: TBD
- Date Range: TBD

Common Failure Patterns:
[To be analyzed after baseline run]

IMPROVEMENTS
============
[To be updated as optimizations are applied]

METHODOLOGY
===========
Metric: Result-set equality (order-insensitive)
Test Set: 12 hand-authored questions with gold SQL and expected result-sets
Categories: Lookup, Filter, Join, Aggregation, Date Range
Environment: MySQL 8.0, claude-sonnet-5, Python executor
Self-Correction: Enabled (1 retry with DB error feedback)
EOF
ls -la docs/accuracy_report.txt
git add docs/accuracy_report.txt
git commit -m "feat: baseline accuracy measurement template

- Evaluation harness ready with 12 gold test cases
- Accuracy report structure for before/after comparison
- Methodology documented"
EOF
