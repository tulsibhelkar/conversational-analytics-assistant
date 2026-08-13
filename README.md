# Conversational Analytics Assistant

A natural-language analytics application that allows users to ask business questions about sales data and receive SQL results, interactive visualizations, and concise business insights.

## Demo

**Business Question → SQL Query → Analysis → Visualization → Business Insight**

[▶ Watch Demo Video](demo/Conversational_Analytics_Assistant_Demo.mp4)

## Overview

The Conversational Analytics Assistant provides a simple way to explore sales data using plain-English business questions.

Instead of manually writing SQL queries or navigating multiple dashboard filters, users can ask questions such as:

- Which region has the highest revenue?
- What are the top 5 best-selling products?
- Show me the monthly revenue trend.
- How does discount percentage affect average revenue?

The application converts supported questions into read-only SQL queries, executes them against a SQLite sales database, and presents the results through interactive visualizations, tables, and business insights.

## Key Features

- Natural-language business queries
- SQL query generation
- Read-only SQL execution
- SQL safety validation
- Interactive Plotly visualizations
- Query result tables
- Business insight generation
- Regional sales analysis
- Product and category analysis
- Customer segment analysis
- Monthly revenue trend analysis
- Discount impact analysis

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and analytics logic |
| Streamlit | Interactive web application |
| SQLite | Relational database |
| SQL | Data querying and analysis |
| Pandas | Data processing |
| NumPy | Synthetic data generation |
| Plotly | Interactive visualizations |

## Dataset

The project uses a synthetic retail sales dataset containing approximately 4,000 records.

### Key Fields

- Order ID
- Order Date
- Customer ID
- Customer Segment
- Region
- Category
- Product
- Quantity
- Unit Price
- Discount Percentage
- Revenue

## Analytics Covered

- Total revenue analysis
- Revenue by region
- Revenue by category
- Product performance
- Top-selling products
- Customer segment analysis
- Monthly revenue trends
- Discount and revenue analysis

## Workflow

```text
Business Question
        ↓
Natural Language Processing
        ↓
SQL Query Generation
        ↓
SQL Safety Validation
        ↓
SQLite Database
        ↓
Data Analysis
        ↓
Visualization + Business Insight

```text
conversational-analytics-assistant/
│
├── app.py
├── nl_to_sql.py
├── insights.py
├── db_setup.py
├── requirements.txt
├── README.md
│
├── demo/
│   └── Conversational_Analytics_Assistant_Demo.mp4
│
└── data/
    ├── generate_data.py
    └── sales_data.csv
