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

        # Get unique orders
        unique_orders = df.drop_duplicates(subset="order_id")
        total_orders = len(unique_orders)
        vine_orders = unique_orders["is_vine"].sum()
        retail_orders = total_orders - vine_orders
        pending_orders = unique_orders[unique_orders["status"] == "pending"].shape[0]

        # Vine units ordered: all vine lines summed
        vine_units_ordered = df[df["is_vine"]]["quantity"].sum()

        # Retail units ordered: sum max quantity per retail order_id
        retail_order_ids = unique_orders[~unique_orders["is_vine"]]["order_id"].tolist()
        retail_units_df = df[df["order_id"].isin(retail_order_ids) & (~df["is_vine"])]
        retail_units_ordered = (
            retail_units_df.groupby("order_id")["quantity"].max().sum()
        )

        shipped_vine_units = df[(df["is_vine"]) & (df["status"] == "shipped")]["quantity"].sum()
        shipped_retail_units = df[(~df["is_vine"]) & (df["status"] == "shipped")]["quantity"].sum()
        pending_units = df[df["status"] == "pending"]["quantity"].sum()

        # Row 1
        row1 = st.columns(4)
        row1[0].metric("Total Orders", total_orders)
        row1[1].metric("Retail Orders", retail_orders)
        row1[2].metric("Vine Orders", vine_orders)
        row1[3].metric("Pending Orders", pending_orders)

        # Row 2
        row2 = st.columns(4)
        row2[0].metric("FBA Vine Units Sent", vine_units_sent)
        row2[1].metric("Vine Units Enrolled", vine_units_enrolled)
        row2[2].metric("Vine Units Ordered", vine_units_ordered)
        row2[3].metric("Retail Units Ordered", retail_units_ordered)

        # Row 3
        row3 = st.columns(4)
        row3[0].metric("Shipped Vine Units", shipped_vine_units)
        row3[1].metric("Shipped Retail Units", shipped_retail_units)
        row3[2].metric("Pending Units", pending_units)
        row3[3].markdown("")  # empty placeholder to align layout

        st.markdown("### Full Order Data")
        st.dataframe(df)
