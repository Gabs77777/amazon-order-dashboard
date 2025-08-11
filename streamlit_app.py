import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")

st.markdown(
    "<h1 style='color:white; font-size:36px;'>Amazon Order Dashboard</h1>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Sanitize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '-')

    # Drop rows with missing required fields
    df = df.dropna(subset=['order-status', 'fulfillment-channel'])

    # Classify Vine vs Retail based on 'sales-channel'
    df['order-type'] = df['sales-channel'].apply(lambda x: 'Vine' if 'vine' in str(x).lower() else 'Retail')

    # Count order types
    total_orders = df['amazon-order-id'].nunique()
    vine_orders = df[df['order-type'] == 'Vine']['amazon-order-id'].nunique()
    retail_orders = df[df['order-type'] == 'Retail']['amazon-order-id'].nunique()

    # Count units
    total_units_sent = len(df)
    shipped_df = df[df['order-status'].str.lower() == 'shipped']
    pending_df = df[df['order-status'].str.lower() == 'pending']

    shipped_units = len(shipped_df)
    pending_units = len(pending_df)

    shipped_vine_units = len(shipped_df[shipped_df['order-type'] == 'Vine'])
    shipped_retail_units = len(shipped_df[shipped_df['order-type'] == 'Retail'])

    pending_orders = pending_df['amazon-order-id'].nunique()

    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", total_orders)
    col2.metric("Retail Orders", retail_orders)
    col3.metric("Vine Orders", vine_orders)

    col4, col5, col6 = st.columns(3)
    col4.metric("FBA Vine Units Sent", total_units_sent)
    col5.metric("Shipped Units", shipped_units)
    col6.metric("Pending Units", pending_units)

    col7, col8, col9 = st.columns(3)
    col7.metric("Shipped Vine Units", shipped_vine_units)
    col8.metric("Shipped Retail Units", shipped_retail_units)
    col9.metric("Pending Orders", pending_orders)

    # Data preview
    st.markdown("---")
    st.subheader("Full Order Data")
    st.dataframe(df)
