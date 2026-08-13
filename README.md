# Conversational Analytics Assistant

Ask a business question in plain English ("Which region had the highest revenue?") and get back the SQL query, a chart, and a short auto-generated insight — instead of digging through a static dashboard.


## How it works

1. Sample retail sales data is generated and loaded into a local SQLite DB.
2. User types a question → `nl_to_sql.py` converts it to a SQL `SELECT` query.
   - If an `ANTHROPIC_API_KEY` is set,
   - Otherwise a small rule-based keyword matcher handles common question types, so the app still works with no API key / no internet.
3. The generated SQL is checked (`is_safe_sql`) so only read-only `SELECT` statements can ever run — no chance of the LLM writing something destructive.
4. The query runs, results come back as a chart (bar/line depending on the data shape) + a table.
5. `insights.py` generates a 1-2 line written insight under the chart, same LLM-or-fallback pattern.

## Folder structure

```
conversational-analytics-assistant/
├── app.py              # Streamlit app (the UI)
├── nl_to_sql.py         # question -> SQL logic + safety check
├── insights.py          # result -> written insight logic
├── db_setup.py           # loads CSV into SQLite
├── data/
│   ├── generate_data.py  # creates the sample dataset
│   └── sales_data.csv    # generated sample data (4000 orders, 2023-2025)
├── requirements.txt
├── .env.example
└── README.md
```

## Setup & run

```bash
# 1. clone / unzip this folder, then cd into it
cd conversational-analytics-assistant

# 2. create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. (optional) enable full LLM mode
cp .env.example .env
# edit .env and paste your ANTHROPIC_API_KEY
# skip this step and the app just runs on the rule-based fallback

# 5. generate the sample data (already included, only needed if you want to regenerate)
python data/generate_data.py

# 6. build the database
python db_setup.py

# 7. launch the app
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## Try asking

- "Which region has the highest revenue?"
- "What are the top 5 best-selling products?"
- "Show me the monthly revenue trend"
- "How does discount percentage affect average revenue?"
- "Revenue breakdown by customer segment"

## Notes / things I'd improve with more time

- Rule-based fallback only covers ~7 question patterns — real LLM mode handles anything.
- Swap SQLite for Postgres/MySQL by changing the connection in `db_setup.py` / `app.py` if using a bigger dataset.
- Could add query result caching so repeated questions don't re-hit the DB.
- Chart-type selection is a simple heuristic right now (date column → line, else bar) — could be smarter.

## Resume line

> Built an LLM-powered natural language analytics assistant that converts plain-English business questions into SQL, executes them safely, and auto-generates written insights — reducing ad-hoc reporting turnaround.
