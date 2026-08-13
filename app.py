"""
Conversational Analytics Assistant

Ask business questions in plain English.
The application converts questions into SQL,
runs them against the sales database, and
returns charts, tables, and insights.

Run:
    streamlit run app.py
"""

import sqlite3
import time

import pandas as pd
import plotly.express as px
import streamlit as st

from nl_to_sql import nl_to_sql, UnsafeSQLError
from insights import generate_insight



DB_PATH = "analytics.db"

st.set_page_config(
    page_title="Conversational Analytics Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)



st.markdown(
    """
    <style>

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .main-title {
        font-size: 2.15rem;
        font-weight: 700;
        color: #F0F2F5;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }

    .main-subtitle {
        color: #8B949E;
        font-size: 0.98rem;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 1.12rem;
        font-weight: 650;
        color: #F0F2F5;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .kpi-card {
        background: linear-gradient(145deg, #161B22, #11161D);
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 18px 20px;
        min-height: 105px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.20);
        transition: 0.2s ease;
    }

    .kpi-card:hover {
        border-color: #4B5563;
        transform: translateY(-1px);
    }

    .kpi-label {
        color: #8B949E;
        font-size: 0.82rem;
        font-weight: 500;
        margin-bottom: 8px;
    }

    .kpi-value {
        color: #F0F2F5;
        font-size: 1.55rem;
        font-weight: 700;
    }

    .question-card {
        background: #11161D;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 18px 20px 8px 20px;
        margin-top: 22px;
        margin-bottom: 20px;
    }

    .question-title {
        color: #F0F2F5;
        font-size: 1rem;
        font-weight: 650;
        margin-bottom: 7px;
    }

    .question-description {
        color: #8B949E;
        font-size: 0.85rem;
        margin-bottom: 12px;
    }

    .insight-card {
        background: #11161D;
        border: 1px solid #30363D;
        border-left: 4px solid #3B82F6;
        border-radius: 10px;
        padding: 16px 18px;
        margin-top: 18px;
        margin-bottom: 15px;
    }

    .insight-heading {
        color: #60A5FA;
        font-size: 0.9rem;
        font-weight: 650;
        margin-bottom: 6px;
    }

    .insight-text {
        color: #D1D5DB;
        font-size: 0.93rem;
        line-height: 1.5;
    }

    section[data-testid="stSidebar"] {
        background: #0D1117;
        border-right: 1px solid #30363D;
    }

    .stButton > button {
        border-radius: 7px;
        font-weight: 550;
        border: 1px solid #30363D;
    }

    div[data-baseweb="input"] {
        border-radius: 8px;
    }

    details {
        border: 1px solid #30363D !important;
        border-radius: 9px !important;
        background: #11161D !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #30363D;
        border-radius: 9px;
        overflow: hidden;
    }

    hr {
        border-color: #21262D !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)



def get_connection():
    return sqlite3.connect(DB_PATH)


def run_query(sql: str) -> pd.DataFrame:
    """Execute SQL and return the result as a DataFrame."""
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()


def get_database_stats():
    """Get summary statistics for KPI cards."""
    conn = get_connection()
    try:
        total_orders = pd.read_sql_query(
            "SELECT COUNT(DISTINCT order_id) AS value FROM sales", conn
        ).iloc[0]["value"]

        total_revenue = pd.read_sql_query(
            "SELECT SUM(revenue) AS value FROM sales", conn
        ).iloc[0]["value"]

        total_products = pd.read_sql_query(
            "SELECT COUNT(DISTINCT product) AS value FROM sales", conn
        ).iloc[0]["value"]

        total_regions = pd.read_sql_query(
            "SELECT COUNT(DISTINCT region) AS value FROM sales", conn
        ).iloc[0]["value"]

        return (
            int(total_orders),
            float(total_revenue or 0),
            int(total_products),
            int(total_regions),
        )
    finally:
        conn.close()




def create_chart(df: pd.DataFrame):
    """Create a colorful, interactive Plotly chart automatically based on
    the query result shape."""
    if df.empty or df.shape[1] < 2:
        return None

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

    if not numeric_cols or not non_numeric_cols:
        return None

    label_col = non_numeric_cols[0]
    value_col = numeric_cols[0]

    is_time_series = (
        "month" in label_col.lower()
        or "date" in label_col.lower()
        or "year" in label_col.lower()
    )

    if is_time_series:
        fig = px.area(
            df,
            x=label_col,
            y=value_col,
            markers=True,
            color_discrete_sequence=["#3B82F6"],
        )
        fig.update_traces(
            line=dict(width=3, color="#60A5FA"),
            marker=dict(size=8, color="#93C5FD", line=dict(width=1, color="#1D4ED8")),
            fillcolor="rgba(59, 130, 246, 0.18)",
            hovertemplate=f"<b>%{{x}}</b><br>{value_col}: %{{y:,.2f}}<extra></extra>",
        )
    elif len(df) <= 20:
        fig = px.bar(
            df,
            x=label_col,
            y=value_col,
            color=value_col,
            color_continuous_scale=[
                "#1E3A8A", "#2563EB", "#3B82F6", "#60A5FA",
                "#38BDF8", "#22D3EE", "#34D399", "#FBBF24",
            ],
            text=value_col,
        )
        fig.update_traces(
            marker_line_width=0,
            opacity=0.95,
            texttemplate="%{text:,.0f}",
            textposition="outside",
            hovertemplate=f"<b>%{{x}}</b><br>{value_col}: %{{y:,.2f}}<extra></extra>",
        )
        fig.update_layout(coloraxis_showscale=False)
    else:
        return None

    fig.update_layout(
        height=440,
        margin=dict(l=20, r=20, t=30, b=30),
        paper_bgcolor="#11161D",
        plot_bgcolor="#11161D",
        font=dict(color="#D1D5DB"),
        xaxis=dict(title=None, showgrid=False, linecolor="#30363D"),
        yaxis=dict(title=None, showgrid=True, gridcolor="#21262D", linecolor="#30363D"),
        hovermode="x unified" if is_time_series else "closest",
        hoverlabel=dict(bgcolor="#1F2937", font_size=13, font_color="#F0F2F5"),
        transition=dict(duration=400, easing="cubic-in-out"),
    )
    return fig



SAMPLE_QUESTIONS = [
    "Which region has the highest revenue?",
    "What are the top 5 best-selling products?",
    "Show me the monthly revenue trend",
    "How does discount percentage affect average revenue?",
    "Revenue breakdown by customer segment",
]



with st.sidebar:
    st.markdown("## Conversational Analytics")
    st.caption("Natural language sales analytics")
    st.divider()

    st.markdown("### Data Source")
    st.markdown(
        """
        **Database**
        SQLite

        **Table**
        `sales`

        **Query Engine**
        Rule-based SQL
        """
    )
    st.divider()

    st.markdown("### Example Questions")
    for index, question_text in enumerate(SAMPLE_QUESTIONS):
        if st.button(question_text, key=f"sample_{index}", use_container_width=True):
            st.session_state["pending_question"] = question_text
            st.session_state["auto_run"] = True

    st.divider()
    st.caption(
        "Ask questions about revenue, regions, products, "
        "categories, discounts, and customer segments."
    )




st.markdown(
    """
    <div class="main-title">Conversational Analytics Assistant</div>
    <div class="main-subtitle">
        Ask business questions about your sales data and get
        SQL results, visualizations, and insights.
    </div>
    """,
    unsafe_allow_html=True,
)




try:
    total_orders, total_revenue, total_products, total_regions = get_database_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Orders</div>
                <div class="kpi-value">{total_orders:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Revenue</div>
                <div class="kpi-value">${total_revenue:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Products</div>
                <div class="kpi-value">{total_products:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Regions</div>
                <div class="kpi-value">{total_regions:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

except Exception as e:
    st.warning(f"Database statistics could not be loaded: {e}")



st.markdown(
    """
    <div class="question-card">
        <div class="question-title">Ask your data</div>
        <div class="question-description">
            Enter a business question in plain English.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

default_question = st.session_state.pop("pending_question", "")

question = st.text_input(
    "Question",
    value=default_question,
    placeholder="Example: Which region generated the highest revenue?",
    label_visibility="collapsed",
)

button_col1, button_col2, empty_col = st.columns([1, 1, 6])

with button_col1:
    ask_clicked = st.button("Ask", type="primary", use_container_width=True)

with button_col2:
    clear_clicked = st.button("Clear", use_container_width=True)

auto_run = st.session_state.pop("auto_run", False)




if "history" not in st.session_state:
    st.session_state["history"] = []

if clear_clicked:
    st.session_state["history"] = []
    st.rerun()




if (ask_clicked or auto_run) and question.strip():
    with st.spinner("Analyzing your question..."):
        start_time = time.time()
        try:
            sql, sql_source = nl_to_sql(question)
            df = run_query(sql)
            insight, insight_source = generate_insight(question, df)
            elapsed = time.time() - start_time

            st.session_state["history"].insert(
                0,
                {
                    "question": question,
                    "sql": sql,
                    "sql_source": sql_source,
                    "df": df,
                    "insight": insight,
                    "insight_source": insight_source,
                    "elapsed": elapsed,
                },
            )
        except UnsafeSQLError:
            st.error(
                "The generated SQL query failed the safety check. "
                "Please rephrase your question."
            )
        except Exception as e:
            st.error(f"Something went wrong: {e}")




if not st.session_state["history"]:
    st.markdown(
        """
        <div style="
            background:#11161D;
            border:1px solid #30363D;
            border-radius:12px;
            padding:45px 20px;
            text-align:center;
            margin-top:20px;
        ">
            <div style="font-size:1.15rem; font-weight:650; color:#F0F2F5;">
                Start exploring your sales data
            </div>
            <div style="color:#8B949E; margin-top:8px; font-size:0.9rem;">
                Ask a question above or select an example from the sidebar.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



for item in st.session_state["history"]:
    st.markdown(
        '<div class="section-title">Analysis Result</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="
            background:#11161D;
            border:1px solid #30363D;
            border-radius:9px;
            padding:12px 16px;
            margin-bottom:15px;
        ">
            <span style="color:#8B949E; font-size:0.82rem;">QUESTION</span>
            <br>
            <span style="color:#F0F2F5; font-size:1rem; font-weight:600;">
                {item['question']}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(f"View SQL Query  •  rule-based  •  {item['elapsed']:.2f}s"):
        st.code(item["sql"], language="sql")

    if item["df"].empty:
        st.warning("No results were found for this question.")
    else:
        chart_col, table_col = st.columns([1.7, 1])

        with chart_col:
            st.markdown("#### Visualization")
            fig = create_chart(item["df"])
            if fig:
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": True, "displaylogo": False},
                )
            else:
                st.dataframe(item["df"], use_container_width=True, hide_index=True)

        with table_col:
            st.markdown("#### Query Results")
            st.dataframe(
                item["df"], use_container_width=True, height=390, hide_index=True
            )

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-heading">BUSINESS INSIGHT</div>
            <div class="insight-text">{item['insight']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()