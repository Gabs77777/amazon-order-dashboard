import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

vine_units_sent = st.number_input("FBA Vine Units Sent", min_value=0, step=1)
vine_units_enrolled = st.number_input("Vine Units Enrolled", min_value=0, step=1)
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.lower().str.strip()

    rename_map = {
        "amazon-order-id": "order_id",
        "order-status": "status",
        "quantity": "quantity",
        "promotion-ids": "promotion_ids"
    }
    df = df.rename(columns=rename_map)

    required_cols = {"order_id", "status", "quantity"}
    if not required_cols.issubset(df.columns):
        st.error(f"Missing required columns: {', '.join(required_cols - set(df.columns))}")
    else:
        df["status"] = df["status"].astype(str).str.lower().str.strip()
        df["promotion_ids"] = df["promotion_ids"].fillna("").astype(str)
        df["is_vine"] = df["promotion_ids"].str.contains("vine.enrollment", case=False)

        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)

        # Unique orders
        unique_orders = df.drop_duplicates(subset="order_id")

        total_orders = len(unique_orders)
        vine_orders = unique_orders["is_vine"].sum()
        retail_orders = total_orders - vine_orders
        pending_orders = unique_orders[unique_orders["status"] == "pending"].shape[0]

        # Retail units based on unique retail order_ids
        unique_retail_order_ids = unique_orders[~unique_orders["is_vine"]]["order_id"].unique()
        retail_units_ordered = df[df["order_id"].isin(unique_retail_order_ids) & (~df["is_vine"])]["quantity"].sum()

        vine_units_ordered = df[df["is_vine"]]["quantity"].sum()
        shipped_vine_units = df[(df["is_vine"]) & (df["status"] == "shipped")]["quantity"].sum()
        shipped_retail_units = df[(~df["is_vine"]) & (df["status"] == "shipped")]["quantity"].sum()
        pending_units = df[df["status"] == "pending"]["quantity"].sum()

        # Row 1: Orders
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Orders", total_orders)
        col2.metric("Retail Orders", retail_orders)
        col3.metric("Vine Orders", vine_orders)
        col4.metric("Pending Orders", pending_orders)

        # Row 2: FBA/Vine
        col5, col6, col7, col8 = st.columns(4)
        col5.metric("FBA Vine Units Sent", vine_units_sent)
        col6.metric("Vine Units Enrolled", vine_units_enrolled)
        col7.metric("Vine Units Ordered", int(vine_units_ordered))
        col8.metric("Retail Units Ordered", int(retail_units_ordered))

        # Row 3: Shipping/Pending
        col9, col10, col11 = st.columns(3)
        col9.metric("Shipped Vine Units", int(shipped_vine_units))
        col10.metric("Shipped Retail Units", int(shipped_retail_units))
        col11.metric("Pending Units", int(pending_units))

        st.markdown("### Full Order Data")
        st.dataframe(df)
