import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Check required columns
    required = ['order-status', 'quantity', 'promotion-ids']
    for col in required:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            st.stop()

    # Define Vine orders strictly
    df['vine'] = df['promotion-ids'].astype(str).str.contains('vine.enrollment', case=False, na=False)
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
    df['order-status'] = df['order-status'].astype(str).str.lower()

    # MANUAL FBA Vine info
    TOTAL_FBA_VINE_UNITS_SENT = 15
    TOTAL_VINE_ENROLLED_UNITS = 14

    # Order counts
    total_orders = len(df)
    vine_orders = df['vine'].sum()
    retail_orders = total_orders - vine_orders
    pending_orders = len(df[df['order-status'] == 'pending'])

    # Unit counts
    vine_units = df[df['vine']]['quantity'].sum()
    retail_units = df[~df['vine']]['quantity'].sum()
    total_units = vine_units + retail_units
    pending_units = df[df['order-status'] == 'pending']['quantity'].sum()
    shipped_units = df[df['order-status'] == 'shipped']['quantity'].sum()
    shipped_vine_units = df[(df['vine']) & (df['order-status'] == 'shipped')]['quantity'].sum()
    shipped_retail_units = df[(~df['vine']) & (df['order-status'] == 'shipped')]['quantity'].sum()

    # Dashboard
    st.subheader("Orders")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", total_orders)
    col2.metric("Retail Orders", retail_orders)
    col3.metric("Vine Orders", vine_orders)

    st.subheader("Units")
    col4, col5, col6 = st.columns(3)
    col4.metric("FBA Vine Units Sent", TOTAL_FBA_VINE_UNITS_SENT)
    col5.metric("Vine Units Enrolled", TOTAL_VINE_ENROLLED_UNITS)
    col6.metric("Vine Units (Ordered)", vine_units)

    col7, col8, col9 = st.columns(3)
    col7.metric("Retail Units (Ordered)", retail_units)
    col8.metric("Total Units Ordered", total_units)
    col9.metric("Pending Units", pending_units)

    col10, col11, col12 = st.columns(3)
    col10.metric("Shipped Units", shipped_units)
    col11.metric("Shipped Vine Units", shipped_vine_units)
    col12.metric("Shipped Retail Units", shipped_retail_units)

    st.metric("Pending Orders", pending_orders)

    # Table view
    st.subheader("Full Order Data")
    st.dataframe(df[['amazon-order-id', 'purchase-date', 'order-status', 'quantity', 'promotion-ids', 'vine']], use_container_width=True)
