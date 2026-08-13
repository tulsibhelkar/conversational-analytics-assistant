"""
insights.py
------------
Turns a query result (pandas DataFrame) into a short, human-readable
business insight -- the "so what" line an analyst would actually write
under a chart.

Same two-mode pattern as nl_to_sql.py: use Claude if a key is available,
otherwise fall back to a simple stats-based sentence generator.
"""

import os

import pandas as pd


def _call_claude_for_insight(question: str, df: pd.DataFrame) -> str | None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        sample = df.head(10).to_string(index=False)
        prompt = f"""A business user asked: "{question}"

Here is the query result (a preview):
{sample}

Write ONE short, plain-English business insight (max 2 sentences) a data
analyst would put under this chart in a report. Be specific with numbers
from the table. No preamble, just the insight."""
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[insights] LLM call failed, falling back to stats summary: {e}")
        return None


def _rule_based_insight(df: pd.DataFrame) -> str:
    if df.empty:
        return "No data matched this question -- try rephrasing it."

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        return "Here's the result -- no numeric column to summarize automatically."

    # the "interesting" number is usually the last numeric column (the
    # aggregate, e.g. total_revenue/avg_revenue) rather than a grouping
    # key like discount_pct that also happens to be numeric.
    metric_col = numeric_cols[-1]
    # the label is just whatever the first column is, even if it's numeric
    # (e.g. discount_pct grouped on its own is still a meaningful label)
    label_col = df.columns[0] if df.columns[0] != metric_col else None

    sorted_df = df.sort_values(metric_col, ascending=False).reset_index(drop=True)
    top_row = sorted_df.iloc[0]
    total = df[metric_col].sum()
    share = (top_row[metric_col] / total * 100) if total else 0

    if label_col and len(df) > 1:
        return (
            f"'{top_row[label_col]}' leads with {top_row[metric_col]:,.0f} "
            f"({share:.0f}% of the total shown here), noticeably ahead of the rest."
        )
    elif label_col:
        return f"'{top_row[label_col]}' recorded {top_row[metric_col]:,.0f}."
    else:
        return f"Result: {top_row[metric_col]:,.2f}."


def generate_insight(question: str, df: pd.DataFrame) -> tuple[str, str]:
    """Returns (insight_text, source)."""
    insight = _call_claude_for_insight(question, df)
    if insight:
        return insight, "llm"
    return _rule_based_insight(df), "rule-based"
