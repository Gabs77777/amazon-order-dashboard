import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

# Input fields for known Vine shipment info
vine_units_sent = st.number_input("FBA Vine Units Sent", min_value=0, step=1)
vine_units_enrolled = st.number_input("Vine Units Enrolled", min_value=0, step=1)

# File upload
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Rename known columns
    rename_map = {
        "amazon-order-id": "order_id",
        "order-status": "status",
        "quantity": "quantity",
        "promotion-ids": "promotion_ids"
    }
    df = df.rename(columns=rename_map)

    required_columns = {"order_id", "status", "quantity"}
    if not required_columns.issubset(df.columns):
        st.error(f"Missing required column(s): {', '.join(required_columns - set(df.columns))}")
    else:
        # Normalize status
        df["status"] = df["status"].astype(str).str.strip().str.lower()

        # Detect Vine orders
        df["is_vine"] = df["promotion_ids"].astype(str).str.contains("vine.enrollment", case=False, na=False)

        # Counts
        total_orders = len(df)
        vine_orders = df["is_vine"].sum()
        retail_orders = total_orders - vine_orders

        vine_units_ordered = df[df["is_vine"]]["quantity"].sum()
        retail_units_ordered = df[~df["is_vine"]]["quantity"].sum()

        pending_orders = len(df[df["status"] == "pending"])
        shipped_retail_units = df[(df["status"] == "shipped") & (~df["is_vine"])]["quantity"].sum()
        shipped_vine_units = df[(df["status"] == "shipped") & (df["is_vine"])]["quantity"].sum()

        pending_units = df[df["status"] == "pending"]["quantity"].sum()

        # Metrics display
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Orders", total_orders)
        col2.metric("Retail Orders", retail_orders)
        col3.metric("Vine Orders", vine_orders)
        col4.metric("Pending Orders", pending_orders)

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("FBA Vine Units Sent", vine_units_sent)
        col6.metric("Vine Units Enrolled", vine_units_enrolled)
        col7.metric("Vine Units Ordered", vine_units_ordered)
        col8.metric("Retail Units Ordered", retail_units_ordered)

        col9, col10, col11 = st.columns(3)
        col9.metric("Shipped Vine Units", shipped_vine_units)
        col10.metric("Shipped Retail Units", shipped_retail_units)
        col11.metric("Pending Units", pending_units)

        st.markdown("### Full Order Data")
        st.dataframe(df)
