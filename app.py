import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finance Tracker", layout="wide")

st.title("My Wallet App")

uploaded_file = st.file_uploader("Upload your bank CSV", type=["csv"])

rules = {
    "UBER": "Transport",
    "NETFLIX": "Subscriptions",
    "AMAZON": "Shopping",
    "RENT": "Housing",
    "SUPERMARKET": "Groceries",
}

def categorize(description):
    description = str(description).upper()
    for keyword, category in rules.items():
        if keyword in description:
            return category
    return "Uncategorized"

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Raw bank extract")
    st.dataframe(df)

    transactions = pd.DataFrame({
        "date": pd.to_datetime(df["Date"]),
        "description": df["Description"].astype(str),
        "amount": df["Amount"].astype(float),
    })

    transactions["category"] = transactions["description"].apply(categorize)
    transactions["month"] = transactions["date"].dt.to_period("M").astype(str)

    st.subheader("Categorized transactions")
    st.dataframe(transactions)

    report = (
        transactions
        .groupby(["month", "category"])["amount"]
        .sum()
        .reset_index()
    )

    st.subheader("Monthly report")
    st.dataframe(report)

    st.download_button(
        "Download report as CSV",
        report.to_csv(index=False),
        "monthly_report.csv",
        "text/csv"
    )
else:
    st.info("Upload a CSV with columns: Date, Description, Amount")
