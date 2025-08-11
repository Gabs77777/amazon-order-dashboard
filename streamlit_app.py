import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean and normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace('-', '_')

    # Rename specific columns for consistency
    df = df.rename(columns={
        'amazon_order_id': 'order_id',
        'order_status': 'status'
    })

    required = ['order_id', 'status', 'quantity', 'promotion_ids']
    if not all(col in df.columns for col in required):
        st.error("Missing required columns in uploaded file.")
        st.stop()

    # Fix data types
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
    df['status'] = df['status'].astype(str).str.lower()
    df['promotion_ids'] = df['promotion_ids'].astype(str)

    # Detect Vine orders automatically
    df['vine'] = df['promotion_ids'].str.contains('vine', case=False, na=False)

    # Manual sidebar inputs
    st.sidebar.header("Manual Inputs")
    vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", value=15)
    vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", value=14)
    units_left_in_stock = st.sidebar.number_input("FBA Vine Units Remaining", value=vine_units_sent - vine_units_enrolled)

    # Orders
    total_orders = len(df)
    vine_orders = df[df['vine']]['order_id'].nunique()
    retail_orders = total_orders - vine_orders
    pending_orders = len(df[df['status'] == 'pending'])

    # Units
    vine_units = df[df['vine']]['quantity'].sum()
    retail_units = df[~df['vine']]['quantity'].sum()
    total_units = vine_units + retail_units
    pending_units = df[df['status'] == 'pending']['quantity'].sum()

    shipped_vine_units = df[(df['vine']) & (df['status'] == 'shipped')]['quantity'].sum()
    shipped_retail_units = df[(~df['vine']) & (df['status'] == 'shipped')]['quantity'].sum()

    # Display: Orders
    st.markdown("### Orders")
    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Total Orders", total_orders)
    o2.metric("Retail Orders", retail_orders)
    o3.metric("Vine Orders", vine_orders)
    o4.metric("Pending Orders", pending_orders)

    # Display: Units
    st.markdown("### Units")
    u1, u2, u3, u4 = st.columns(4)
    u1.metric("FBA Vine Units Sent", vine_units_sent)
    u2.metric("Vine Units Enrolled", vine_units_enrolled)
    u3.metric("Vine Units Ordered", vine_units)
    u4.metric("Retail Units Ordered", retail_units)

    u5, u6, u7, u8 = st.columns(4)
    u5.metric("Total Units Ordered", total_units)
    u6.metric("Pending Units", pending_units)
    u7.metric("Shipped Vine Units", shipped_vine_units)
    u8.metric("Shipped Retail Units", shipped_retail_units)

    u9, _, _, _ = st.columns(4)
    u9.metric("FBA Vine Units Left", units_left_in_stock)

    # Show clean table
    st.markdown("### Order Breakdown")
    st.dataframe(df[['order_id', 'purchase_date', 'status', 'quantity', 'promotion_ids', 'vine']], use_container_width=True)
