import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finance Tracker", layout="wide")

st.title("Personal Finance Tracker")

uploaded_file = st.file_uploader(
    "Upload bank extract",
    type=["csv", "xlsx"]
)

rules = {
    "CONTINENTE": "Groceries",
    "PIZZAHUT": "Dining",
    "UBER": "Transport",
    "NETFLIX": "Subscriptions",
    "AMAZON": "Shopping",
    "ALIEXPRESS": "Shopping",
    "FARMACIA": "Health",
    "ADIDAS": "Shopping",
    "LEFTIES": "Shopping",
    "CELEIRO": "Groceries",
}

def categorize(description):
    description = str(description).upper()
    for keyword, category in rules.items():
        if keyword in description:
            return category
    return "Uncategorized"

def read_bank_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    if file_name.endswith(".xlsx"):
        raw = pd.read_excel(uploaded_file, header=None)

        # In your file, the real table header starts at row 8 in Excel
        header_row = raw[raw.iloc[:, 0].astype(str).str.contains("Data Lanc.", na=False)].index[0]

        df = pd.read_excel(uploaded_file, header=header_row)

        return df

    raise ValueError("Unsupported file format")

if uploaded_file is not None:
    df = read_bank_file(uploaded_file)

    st.subheader("Raw bank extract")
    st.dataframe(df)

    transactions = pd.DataFrame({
        "date": pd.to_datetime(df["Data Lanc."], errors="coerce"),
        "value_date": pd.to_datetime(df["Data Valor"], errors="coerce"),
        "description": df["Descrição"].astype(str),
        "amount": pd.to_numeric(df["Valor"], errors="coerce"),
        "balance": pd.to_numeric(df["Saldo"], errors="coerce"),
    })

    transactions = transactions.dropna(subset=["date", "amount"])

    transactions["type"] = transactions["amount"].apply(
        lambda x: "Income" if x > 0 else "Expense"
    )

    transactions["category"] = transactions["description"].apply(categorize)
    transactions["month"] = transactions["date"].dt.to_period("M").astype(str)

    st.subheader("Categorized transactions")
    st.dataframe(transactions)

    monthly_report = (
        transactions
        .groupby(["month", "category", "type"])["amount"]
        .sum()
        .reset_index()
        .sort_values(["month", "type", "category"])
    )

    st.subheader("Monthly report")
    st.dataframe(monthly_report)

    category_report = (
        transactions
        .groupby("category")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount")
    )

    st.subheader("Spending by category")
    st.bar_chart(category_report.set_index("category"))

    st.download_button(
        "Download categorized transactions",
        transactions.to_csv(index=False),
        "categorized_transactions.csv",
        "text/csv"
    )

    st.download_button(
        "Download monthly report",
        monthly_report.to_csv(index=False),
        "monthly_report.csv",
        "text/csv"
    )

else:
    st.info("Upload your bank extract file. This version supports CSV and XLSX.")
