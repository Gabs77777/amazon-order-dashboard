import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Ensure required columns exist
    required_cols = ['order-status', 'quantity', 'promotion-ids']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            st.stop()

    # Add vine flag (checkbox column exists or infer from promotion-ids)
    if 'vine' not in df.columns:
        df['vine'] = df['promotion-ids'].astype(str).str.contains('vine', case=False, na=False)

    # Ensure quantity is numeric
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)

    # Total orders
    total_orders = len(df)
    vine_orders = df['vine'].sum()
    retail_orders = total_orders - vine_orders

    # Total units
    fba_vine_units_sent = df[df['vine']]['quantity'].sum()
    shipped_units = df[df['order-status'].str.lower() == 'shipped']['quantity'].sum()
    pending_units = df[df['order-status'].str.lower() == 'pending']['quantity'].sum()

    shipped_vine_units = df[(df['vine']) & (df['order-status'].str.lower() == 'shipped')]['quantity'].sum()
    shipped_retail_units = df[(~df['vine']) & (df['order-status'].str.lower() == 'shipped')]['quantity'].sum()

    pending_orders = len(df[df['order-status'].str.lower() == 'pending'])

    # Orders summary
    st.subheader("Orders")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", total_orders)
    col2.metric("Retail Orders", retail_orders)
    col3.metric("Vine Orders", vine_orders)

    # Units summary
    st.subheader("Units")
    col4, col5, col6 = st.columns(3)
    col4.metric("FBA Vine Units Sent", fba_vine_units_sent)
    col5.metric("Shipped Units", shipped_units)
    col6.metric("Pending Units", pending_units)

    col7, col8, col9 = st.columns(3)
    col7.metric("Shipped Vine Units", shipped_vine_units)
    col8.metric("Shipped Retail Units", shipped_retail_units)
    col9.metric("Pending Orders", pending_orders)

    # Display selected table columns
    st.subheader("Full Order Data")
    display_columns = [
        'amazon-order-id',
        'purchase-date',
        'order-status',
        'quantity',
        'promotion-ids',
        'vine'
    ]
    display_columns = [col for col in display_columns if col in df.columns]
    st.dataframe(df[display_columns], use_container_width=True)
