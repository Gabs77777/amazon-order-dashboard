import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

# Sidebar: Manual inputs
fba_vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", min_value=0, value=15)
vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", min_value=0, value=14)

# File uploader
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "-")

    # Ensure 'quantity' is numeric and filled
    if "quantity" not in df.columns:
        df["quantity"] = 1
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)

    # Classify Vine orders
    def is_vine(promo_id):
        if isinstance(promo_id, str):
            return "vine.enrollment" in promo_id.lower()
        return False

    df["vine"] = df["promotion-ids"].apply(is_vine)

    # Split into Vine and Retail
    vine_orders_df = df[df["vine"] == True]
    retail_orders_df = df[df["vine"] == False]

    # Metrics
    total_orders = len(df)
    retail_orders = len(retail_orders_df)
    vine_orders = len(vine_orders_df)
    pending_orders = df["order-status"].str.lower().eq("pending").sum()

    vine_units_ordered = vine_orders_df["quantity"].sum()
    retail_units_ordered = retail_orders_df["quantity"].sum()
    total_units_ordered = vine_units_ordered + retail_units_ordered

    shipped_vine_units = vine_orders_df[vine_orders_df["order-status"].str.lower() == "shipped"]["quantity"].sum()
    shipped_retail_units = retail_orders_df[retail_orders_df["order-status"].str.lower() == "shipped"]["quantity"].sum()

    pending_units = df[df["order-status"].str.lower() == "pending"]["quantity"].sum()

    # Dashboard
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", total_orders)
    col2.metric("Retail Orders", retail_orders)
    col3.metric("Vine Orders", vine_orders)
    col4.metric("Pending Orders", pending_orders)

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("FBA Vine Units Sent", fba_vine_units_sent)
    col6.metric("Vine Units Enrolled", vine_units_enrolled)
    col7.metric("Vine Units Ordered", vine_units_ordered)
    col8.metric("Retail Units Ordered", retail_units_ordered)

    col9, col10, col11 = st.columns(3)
    col9.metric("Shipped Vine Units", shipped_vine_units)
    col10.metric("Shipped Retail Units", shipped_retail_units)
    col11.metric("Pending Units", pending_units)

    st.subheader("Total Units Ordered")
    st.metric("Total Units", total_units_ordered)

    st.subheader("Full Order Data")
    st.dataframe(df)
