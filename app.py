from __future__ import annotations
from datetime import date
import pandas as pd
import streamlit as st
from sqlalchemy import text
from config.db import get_engine


def _get_date_bounds(engine) -> tuple[date | None, date | None]:
    sql = text("SELECT MIN(txn_date) AS min_date, MAX(txn_date) AS max_date FROM transactions")
    with engine.connect() as conn:
        row = conn.execute(sql).one()
    return row.min_date, row.max_date


def _get_categories(engine) -> list[str]:
    sql = text("SELECT DISTINCT category FROM transactions ORDER BY category")
    with engine.connect() as conn:
        rows = conn.execute(sql).all()
    return [row[0] for row in rows]


def _load_transactions(engine, start_date: date, end_date: date, categories: list[str]) -> pd.DataFrame:
    base_sql = (
        "SELECT txn_date, category, amount, description, account_no, source_file "
        "FROM transactions "
        "WHERE txn_date BETWEEN :start_date AND :end_date"
    )
    params: dict[str, object] = {"start_date": start_date, "end_date": end_date}

    if categories:
        base_sql += " AND category = ANY(:categories)"
        params["categories"] = categories

    base_sql += " ORDER BY txn_date, txn_time"

    return pd.read_sql(text(base_sql), con=engine, params=params, parse_dates=["txn_date"])


def main() -> None:
    st.set_page_config(page_title="SMS Expense Reports", layout="wide")
    st.title("SMS Expense Reports")

    engine = get_engine()

    min_date, max_date = _get_date_bounds(engine)
    if min_date is None or max_date is None:
        st.info("No transactions found yet. Run the ETL to load data.")
        return

    categories = _get_categories(engine)

    col1, col2 = st.columns(2)
    with col1:
        date_range = st.date_input("Date range", value=(min_date, max_date))
    with col2:
        selected_categories = st.multiselect(
            "Category",
            options=categories,
            default=categories,
        )

    if not date_range or len(date_range) != 2:
        st.warning("Please select a valid date range.")
        return

    if not selected_categories:
        st.warning("Select at least one category to see results.")
        return

    start_date, end_date = date_range

    df = _load_transactions(engine, start_date, end_date, selected_categories)
    if df.empty:
        st.info("No results for the selected filters.")
        return

    monthly = (
        df.groupby(pd.Grouper(key="txn_date", freq="MS"))["amount"]
        .sum()
        .reset_index()
        .rename(columns={"txn_date": "month", "amount": "total"})
    )

    weekly = (
        df.groupby(pd.Grouper(key="txn_date", freq="W-MON"))["amount"]
        .sum()
        .reset_index()
        .rename(columns={"txn_date": "week_start", "amount": "total"})
    )

    category_totals = (
        df.groupby("category")["amount"].sum().reset_index().rename(columns={"amount": "total"})
    )

    top3_per_category = (
        df.sort_values(["category", "amount"], ascending=[True, False])
        .groupby("category")
        .head(3)
        .reset_index(drop=True)
    )

    df_monthly = df.copy()
    df_monthly["month"] = df_monthly["txn_date"].dt.to_period("M").dt.to_timestamp()
    month_options = sorted(df_monthly["month"].unique())

    popular_by_count = (
        df.groupby("category").size().reset_index(name="count").sort_values("count", ascending=False)
    )
    popular_by_amount = (
        category_totals.sort_values("total", ascending=False)
    )

    top3_months = (
        monthly.sort_values("total", ascending=False).head(3).reset_index(drop=True)
    )
    top3_months_display = top3_months.copy()
    top3_months_display["month"] = top3_months_display["month"].dt.strftime("%b %Y")

    top3_month_set = set(top3_months["month"].tolist())
    top3_month_details = (
        df_monthly[df_monthly["month"].isin(top3_month_set)]
        .sort_values(["month", "amount"], ascending=[True, False])
        [["month", "txn_date", "amount", "category", "description"]]
        .copy()
    )
    top3_month_details["month"] = top3_month_details["month"].dt.strftime("%b %Y")

    st.subheader("Monthly Spend")
    st.line_chart(monthly.set_index("month"))

    st.subheader("Weekly Spend")
    st.line_chart(weekly.set_index("week_start"))

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Most Popular Category by Count")
        st.bar_chart(popular_by_count.set_index("category"))
    with col_b:
        st.subheader("Most Popular Category by Amount")
        st.bar_chart(popular_by_amount.set_index("category"))

    st.subheader("Top 3 Months by Total Amount")
    st.dataframe(top3_months_display, width="stretch")

    st.subheader("Top 3 Months Transactions")
    st.dataframe(top3_month_details, width="stretch")

    st.subheader("Top 3 Amounts per Category")
    st.dataframe(top3_per_category, width="stretch")

    st.subheader("Top 3 Amounts for Selected Month")
    # default to the latest available month
    latest_index = max(0, len(month_options) - 1)
    selected_month = st.selectbox(
        "Select month for top 3 amounts",
        options=month_options,
        index=latest_index,
        format_func=lambda d: d.strftime("%b %Y"),
    )

    top3_selected_month = (
        df_monthly[df_monthly["month"] == selected_month]
        .sort_values("amount", ascending=False)
        .head(3)
        .reset_index(drop=True)
    )
    st.dataframe(top3_selected_month, width="stretch")

    st.subheader("Filtered Transactions")
    st.dataframe(df, width="stretch")


if __name__ == "__main__":
    main()
