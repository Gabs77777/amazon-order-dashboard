import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

# Input fields
fba_vine_units_sent = st.number_input("FBA Vine Units Sent", min_value=0, step=1, value=0)
vine_units_enrolled = st.number_input("Vine Units Enrolled", min_value=0, step=1, value=0)

# Upload file
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

# Replace this list with your actual Vine order IDs
VINE_ORDER_IDS = [
    "113-2822895-8082085",
    "113-7385029-4926631",
    "113-9310765-6389363",
    "113-3310595-9052851",
]

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("-", "_")

    # Standard column mapping
    df.rename(columns={
        "amazon_order_id": "order_id",
        "order_status": "status",
        "quantity": "quantity",
        "product_name": "product_name"
    }, inplace=True)

    # Ensure required columns
    required_columns = {"order_id", "status", "quantity"}
    if not required_columns.issubset(df.columns):
        st.error("Missing required columns. Please check your spreadsheet.")
    else:
        # Normalize text
        df["order_id"] = df["order_id"].astype(str).str.strip()
        df["status"] = df["status"].astype(str).str.strip().str.lower()
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)

        # Add Vine flag
        df["is_vine"] = df["order_id"].isin(VINE_ORDER_IDS)

        # Summary stats
        total_orders = len(df)
        vine_orders = df[df["is_vine"]]
        retail_orders = df[~df["is_vine"]]

        shipped_vine_units = vine_orders[vine_orders["status"] == "shipped"]["quantity"].sum()
        shipped_retail_units = retail_orders[retail_orders["status"] == "shipped"]["quantity"].sum()
        vine_units_ordered = vine_orders["quantity"].sum()
        retail_units_ordered = retail_orders["quantity"].sum()

        pending_orders = df[df["status"] != "shipped"]
        pending_units = pending_orders["quantity"].sum()

        total_units_ordered = df["quantity"].sum()

        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Orders", total_orders)
        col2.metric("Retail Orders", len(retail_orders))
        col3.metric("Vine Orders", len(vine_orders))
        col4.metric("Pending Orders", len(pending_orders))

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("FBA Vine Units Sent", fba_vine_units_sent)
        col6.metric("Vine Units Enrolled", vine_units_enrolled)
        col7.metric("Vine Units Ordered", vine_units_ordered)
        col8.metric("Retail Units Ordered", retail_units_ordered)

        col9, col10, col11, col12 = st.columns(4)
        col9.metric("Shipped Vine Units", shipped_vine_units)
        col10.metric("Shipped Retail Units", shipped_retail_units)
        col11.metric("Pending Units", pending_units)
        col12.metric("Total Units Ordered", total_units_ordered)

        st.subheader("Full Order Data")
        st.dataframe(df)
