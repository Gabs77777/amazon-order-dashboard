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
    df['is_vine'] = df['promotion-ids'].str.contains(vine_key)

    # Order counts (drop duplicates by order ID)
    total_orders = df['amazon-order-id'].drop_duplicates().nunique()
    retail_orders = df[~df['is_vine']]['amazon-order-id'].drop_duplicates().nunique()
    vine_orders = df[df['is_vine']]['amazon-order-id'].drop_duplicates().nunique()

    # Fulfillment stats
    shipped_df = df[df['order-status'].str.lower() == 'shipped']
    shipped_units = shipped_df['quantity'].sum()
    shipped_vine_units = shipped_df[shipped_df['is_vine']]['quantity'].sum()
    shipped_retail_units = shipped_df[~shipped_df['is_vine']]['quantity'].sum()
    pending_units = df[df['order-status'].str.lower() == 'pending']['quantity'].sum()

    # Display metrics
    st.markdown("### Order Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", total_orders)
    col2.metric("Retail Orders", retail_orders)
    col3.metric("Vine Orders", vine_orders)

    st.markdown("### Fulfillment Summary")
    col4, col5, col6, col7 = st.columns(4)
    col4.metric("Total Shipped Units", int(shipped_units))
    col5.metric("Shipped Vine Units", int(shipped_vine_units))
    col6.metric("Shipped Retail Units", int(shipped_retail_units))
    col7.metric("Pending Units", int(pending_units))

    st.markdown("### Data Preview")
    st.dataframe(df)
