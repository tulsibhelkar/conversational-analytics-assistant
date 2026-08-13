"""
Converts a plain-English question into a safe SQL query.

The application uses a rule-based keyword matcher to identify
common business questions and generate SQLite SELECT queries.

Every generated query is checked before execution to ensure that
only a single read-only SELECT statement is allowed.
"""

import re


class UnsafeSQLError(Exception):
    """Raised when generated SQL fails the safety check."""
    pass


def is_safe_sql(sql: str) -> bool:
    """Allow only a single read-only SELECT statement."""

    cleaned = sql.strip().rstrip(";")

    # Must start with SELECT
    if not cleaned.lower().startswith("select"):
        return False

    # Block dangerous SQL commands
    banned = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "attach",
        "pragma",
        "truncate",
        "--",
        "/*",
        "*/",
    ]

    lowered = cleaned.lower()

    if any(word in lowered for word in banned):
        return False

    # Prevent multiple SQL statements
    if ";" in cleaned:
        return False

    return True


def _rule_based_sql(question: str) -> str:
    """
    Generate SQL using keyword-based rules.

    Supports common analytics questions such as:
    - Top region
    - Top products
    - Revenue by category
    - Monthly revenue trend
    - Discount analysis
    - Customer segment analysis
    - Average order value
    - Total revenue
    """

    q = question.lower().strip()

    # Top / highest revenue by region
    if "region" in q and (
        "top" in q
        or "highest" in q
        or "best" in q
        or "most" in q
    ):
        return """
        SELECT
            region,
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM sales
        GROUP BY region
        ORDER BY total_revenue DESC
        LIMIT 5
        """

    # Top / best-selling products
    if "product" in q and (
        "top" in q
        or "best selling" in q
        or "best-selling" in q
        or "highest" in q
        or "most" in q
    ):
        return """
        SELECT
            product,
            SUM(quantity) AS units_sold,
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM sales
        GROUP BY product
        ORDER BY total_revenue DESC
        LIMIT 5
        """

    # Revenue / sales by category
    if "category" in q and (
        "revenue" in q
        or "sales" in q
    ):
        return """
        SELECT
            category,
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM sales
        GROUP BY category
        ORDER BY total_revenue DESC
        """

    # Monthly / time trend
    if (
        "month" in q
        or "monthly" in q
        or "trend" in q
        or "over time" in q
    ):
        return """
        SELECT
            strftime('%Y-%m', order_date) AS month,
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM sales
        GROUP BY month
        ORDER BY month
        """

    # Discount analysis
    if "discount" in q:
        return """
        SELECT
            discount_pct,
            COUNT(*) AS order_count,
            ROUND(AVG(revenue), 2) AS avg_revenue
        FROM sales
        GROUP BY discount_pct
        ORDER BY discount_pct
        """

    # Customer segment analysis
    if (
        "segment" in q
        or "loyal" in q
        or "new customer" in q
        or "returning" in q
    ):
        return """
        SELECT
            customer_segment,
            COUNT(DISTINCT customer_id) AS customers,
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM sales
        GROUP BY customer_segment
        ORDER BY total_revenue DESC
        """

    # Average Order Value
    if (
        "average order" in q
        or "average order value" in q
        or "aov" in q
    ):
        return """
        SELECT
            ROUND(
                SUM(revenue) * 1.0 / COUNT(DISTINCT order_id),
                2
            ) AS avg_order_value
        FROM sales
        """

    # Total revenue
    if (
        "total revenue" in q
        or ("total" in q and "revenue" in q)
    ):
        return """
        SELECT
            ROUND(SUM(revenue), 2) AS total_revenue
        FROM sales
        """

    # Generic fallback
    return """
    SELECT
        region,
        category,
        ROUND(SUM(revenue), 2) AS total_revenue,
        COUNT(*) AS orders
    FROM sales
    GROUP BY region, category
    ORDER BY total_revenue DESC
    LIMIT 10
    """


def nl_to_sql(question: str) -> tuple[str, str]:
    """
    Convert a natural-language question into a safe SQL query.

    Returns:
        (sql, source)

    source will always be 'rule-based' in this version.
    """

    sql = _rule_based_sql(question)

    if not is_safe_sql(sql):
        raise UnsafeSQLError(
            "Generated SQL failed the safety check."
        )

    return sql, "rule-based"