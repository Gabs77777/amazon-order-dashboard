import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")

st.title("Amazon Order Dashboard")
uploaded_file = st.file_uploader("Upload Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    df['order-status'] = df.get('order-status', '').fillna('')
    df['quantity'] = pd.to_numeric(df.get('quantity', 0), errors='coerce').fillna(0)
    df['promotion-ids'] = df.get('promotion-ids', '').fillna('')
    df['amazon-order-id'] = df.get('amazon-order-id', '').astype(str)

    vine_key = 'vine.enrollment.ada9f609-d98f-4e51-845f-f586ae70b3bd'
    df['is_vine'] = df['promotion-ids'].astype(str).str.contains(vine_key)

    # Use row-level granularity for total units
    total_rows = len(df)
    total_orders = df['amazon-order-id'].nunique()
    total_units = int(df['quantity'].sum())
    shipped_units = int(df[df['order-status'] == 'Shipped']['quantity'].sum())
    pending_units = int(df[df['order-status'] == 'Pending']['quantity'].sum())
    
    vine_rows = df[df['is_vine']]
    retail_rows = df[~df['is_vine']]
    vine_orders = vine_rows['amazon-order-id'].nunique()
    retail_orders = retail_rows['amazon-order-id'].nunique()
    shipped_vine_units = int(vine_rows[vine_rows['order-status'] == 'Shipped']['quantity'].sum())
    shipped_retail_units = int(retail_rows[retail_rows['order-status'] == 'Shipped']['quantity'].sum())

    st.markdown("### Order Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Rows", total_rows)
    col2.metric("Total Orders", total_orders)
    col3.metric("Retail Orders", retail_orders)
    col4.metric("Vine Orders", vine_orders)

    st.markdown("### Fulfillment Summary")
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Total Units", total_units)
    col6.metric("Total Shipped Units", shipped_units)
    col7.metric("Shipped Vine Units", shipped_vine_units)
    col8.metric("Shipped Retail Units", shipped_retail_units)

    st.markdown("### Status Summary")
    col9, col10 = st.columns(2)
    col9.metric("Pending Units", pending_units)
    col10.metric("Pending Orders", df[df['order-status'] == 'Pending']['amazon-order-id'].nunique())

    st.markdown("### Data Preview")
    st.dataframe(df)
