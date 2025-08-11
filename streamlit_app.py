import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Check necessary columns
    required = ['order-status', 'quantity', 'promotion-ids']
    if not all(col in df.columns for col in required):
        st.error("Missing required columns. Make sure the file includes 'order-status', 'quantity', and 'promotion-ids'.")
        st.stop()

    # Convert and clean data
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
    df['order-status'] = df['order-status'].astype(str).str.lower()
    df['vine'] = df['promotion-ids'].astype(str).str.contains('vine.enrollment', case=False, na=False)

    # Manual values
    TOTAL_VINE_UNITS_SENT = 15
    TOTAL_VINE_UNITS_ENROLLED = 14

    # Orders
    total_orders = len(df)
    vine_orders = df['vine'].sum()
    retail_orders = total_orders - vine_orders
    pending_orders = len(df[df['order-status'] == 'pending'])

    # Units
    vine_units = df[df['vine']]['quantity'].sum()
    retail_units = df[~df['vine']]['quantity'].sum()
    total_units = vine_units + retail_units
    pending_units = df[df['order-status'] == 'pending']['quantity'].sum()
    shipped_units = df[df['order-status'] == 'shipped']['quantity'].sum()
    shipped_vine_units = df[(df['vine']) & (df['order-status'] == 'shipped')]['quantity'].sum()
    shipped_retail_units = df[(~df['vine']) & (df['order-status'] == 'shipped')]['quantity'].sum()

    # Display clean 3-column layout
    st.markdown("### Orders")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders", total_orders)
    c2.metric("Retail Orders", retail_orders)
    c3.metric("Vine Orders", vine_orders)

    st.markdown("### Units")
    u1, u2, u3 = st.columns(3)
    u1.metric("FBA Vine Units Sent", TOTAL_VINE_UNITS_SENT)
    u2.metric("Vine Units Enrolled", TOTAL_VINE_UNITS_ENROLLED)
    u3.metric("Vine Units Ordered", vine_units)

    u4, u5, u6 = st.columns(3)
    u4.metric("Retail Units Ordered", retail_units)
    u5.metric("Total Units Ordered", total_units)
    u6.metric("Pending Units", pending_units)

    u7, u8, u9 = st.columns(3)
    u7.metric("Shipped Units", shipped_units)
    u8.metric("Shipped Vine Units", shipped_vine_units)
    u9.metric("Shipped Retail Units", shipped_retail_units)

    st.metric("Pending Orders", pending_orders)

    st.markdown("### Full Order Data")
    st.dataframe(df[['amazon-order-id', 'purchase-date', 'order-status', 'quantity', 'promotion-ids', 'vine']], use_container_width=True)
