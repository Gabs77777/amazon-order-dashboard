import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

# File upload
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

# Manual inputs
fba_vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", min_value=0, value=15)
vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", min_value=0, value=14)

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Force all column names to lowercase for safety
    df.columns = [col.lower() for col in df.columns]

    # Convert promotion-ids to string
    df["promotion-ids"] = df["promotion-ids"].astype(str)

    # Identify Vine orders
    df["is_vine"] = df["promotion-ids"].str.contains("vine.enrollment", case=False, na=False)

    # Split Vine vs Retail orders
    vine_orders_df = df[df["is_vine"]]
    retail_orders_df = df[~df["is_vine"]]

    # Calculate order counts
    total_orders = df["amazon-order-id"].nunique()
    vine_orders = vine_orders_df["amazon-order-id"].nunique()
    retail_orders = retail_orders_df["amazon-order-id"].nunique()
    pending_orders = df[df["order-status"].str.lower() == "pending"]["amazon-order-id"].nunique()

    # Units Ordered
    vine_units_ordered = int(vine_orders_df["quantity"].sum())
    retail_units_ordered = int(retail_orders_df["quantity"].sum())
    total_units_ordered = vine_units_ordered + retail_units_ordered

    # Units Shipped
    shipped_vine_units = int(vine_orders_df[df["order-status"].str.lower() == "shipped"]["quantity"].sum())
    shipped_retail_units = int(retail_orders_df[df["order-status"].str.lower() == "shipped"]["quantity"].sum())
    pending_units = int(df[df["order-status"].str.lower() == "pending"]["quantity"].sum())

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", total_orders)
    col2.metric("Retail Orders", retail_orders)
    col3.metric("Vine Orders", vine_orders)
    col4.metric("Pending Orders", pending_orders)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("FBA Vine Units Sent", fba_vine_units_sent)
    col2.metric("Vine Units Enrolled", vine_units_enrolled)
    col3.metric("Vine Units Ordered", vine_units_ordered)
    col4.metric("Retail Units Ordered", retail_units_ordered)

    col1, col2, col3 = st.columns(3)
    col1.metric("Shipped Vine Units", shipped_vine_units)
    col2.metric("Shipped Retail Units", shipped_retail_units)
    col3.metric("Pending Units", pending_units)

    st.subheader("Total Units Ordered")
    st.metric("Total Units", total_units_ordered)

    st.subheader("Full Order Data")
    st.dataframe(df)
