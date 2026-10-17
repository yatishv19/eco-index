# Eco Index — Prototype

A runnable Flask MVP for a consumer-facing environmental intelligence platform.

## What is included

- Company search
- 15-company demo dataset
- Company dashboard
- Scope 1 / Scope 2 / Scope 3 display
- Emissions trend visualization
- Explainable 0–100 Eco Index
- Company comparison
- Source labels
- JSON API endpoints

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start:

```bash
python app.py
```

5. Open:

http://127.0.0.1:5000

## Important prototype note

The values are a demonstration dataset and should not be presented as verified current corporate emissions. The historical trend in the company page is illustrative. Before a public launch, replace demo values with verified source data and year-by-year reporting.

## Next development phase

Add:
1. PDF sustainability-report upload.
2. AI extraction into structured fields.
3. Validation + source/page references.
4. MySQL/PostgreSQL for production storage.
5. Real year-by-year emissions.
6. Industry-normalized metrics such as emissions intensity.
