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

    required = {"order_id", "status", "quantity"}
    if not required.issubset(df.columns):
        st.error(f"Missing required column(s): {', '.join(required - set(df.columns))}")
    else:
        df["status"] = df["status"].astype(str).str.lower().str.strip()
        df["promotion_ids"] = df["promotion_ids"].astype(str).fillna("")
        df["is_vine"] = df["promotion_ids"].str.contains("vine.enrollment", case=False, na=False)

        total_orders = len(df)
        vine_orders = df["is_vine"].sum()
        retail_orders = total_orders - vine_orders

        vine_units_ordered = int(df[df["is_vine"]]["quantity"].sum())
        retail_units_ordered = int(df[~df["is_vine"]]["quantity"].sum())

        pending_orders = len(df[df["status"] == "pending"])
        shipped_vine_units = int(df[(df["status"] == "shipped") & (df["is_vine"])]["quantity"].sum())
        shipped_retail_units = int(df[(df["status"] == "shipped") & (~df["is_vine"])]["quantity"].sum())
        pending_units = int(df[df["status"] == "pending"]["quantity"].sum())

        row1 = st.columns(4)
        row1[0].metric("Total Orders", total_orders)
        row1[1].metric("Retail Orders", retail_orders)
        row1[2].metric("Vine Orders", vine_orders)
        row1[3].metric("Pending Orders", pending_orders)

        row2 = st.columns(4)
        row2[0].metric("FBA Vine Units Sent", vine_units_sent)
        row2[1].metric("Vine Units Enrolled", vine_units_enrolled)
        row2[2].metric("Vine Units Ordered", vine_units_ordered)
        row2[3].metric("Retail Units Ordered", retail_units_ordered)

        row3 = st.columns(3)
        row3[0].metric("Shipped Vine Units", shipped_vine_units)
        row3[1].metric("Shipped Retail Units", shipped_retail_units)
        row3[2].metric("Pending Units", pending_units)

        st.markdown("### Full Order Data")
        st.dataframe(df)
