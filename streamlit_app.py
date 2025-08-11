import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean columns
    df['order-status'] = df.get('order-status', '').fillna('')
    df['quantity'] = pd.to_numeric(df.get('quantity', 0), errors='coerce').fillna(0)
    df['promotion-ids'] = df.get('promotion-ids', '').fillna('')
    df['amazon-order-id'] = df.get('amazon-order-id', '').astype(str)

    # Detect Vine orders
    vine_key = 'vine.enrollment.ada9f609-d98f-4e51-845f-f586ae70b3bd'
    df['is_vine'] = df['promotion-ids'].astype(str).str.contains(vine_key)

    # Group by order ID and summarize
    order_summary = (
        df.groupby('amazon-order-id')
        .agg({
            'is_vine': 'max',
            'quantity': 'sum',
            'order-status': lambda x: list(x)
        })
        .reset_index()
    )

    order_summary['type'] = order_summary['is_vine'].apply(lambda x: 'Vine' if x else 'Retail')
    order_summary['shipped'] = order_summary['order-status'].apply(lambda s: 'Shipped' in s)
    order_summary['pending'] = order_summary['order-status'].apply(lambda s: 'Pending' in s)

    # Subsets
    vine_orders = order_summary[order_summary['type'] == 'Vine']
    retail_orders = order_summary[order_summary['type'] == 'Retail']
    shipped_vine = vine_orders[vine_orders['shipped']]
    shipped_retail = retail_orders[retail_orders['shipped']]

    # Units summary
    total_shipped_units = df[df['order-status'] == 'Shipped']['quantity'].sum()
    shipped_vine_units = df[(df['order-status'] == 'Shipped') & (df['promotion-ids'].str.contains(vine_key))]['quantity'].sum()
    shipped_retail_units = df[(df['order-status'] == 'Shipped') & (~df['promotion-ids'].str.contains(vine_key))]['quantity'].sum()
    pending_units = df[df['order-status'] == 'Pending']['quantity'].sum()

    # Metrics layout - numbers first
    st.subheader("Order Summary")
    summary_cols = st.columns(3)
    summary_cols[0].metric("Total Orders", len(order_summary))
    summary_cols[1].metric("Retail Orders", len(retail_orders))
    summary_cols[2].metric("Vine Orders", len(vine_orders))

    st.subheader("Fulfillment Summary")
    fulfillment_cols = st.columns(4)
    fulfillment_cols[0].metric("Total Shipped Units", total_shipped_units)
    fulfillment_cols[1].metric("Shipped Vine Units", shipped_vine_units)
    fulfillment_cols[2].metric("Shipped Retail Units", shipped_retail_units)
    fulfillment_cols[3].metric("Pending Units", pending_units)

    # Show table last
    st.subheader("Data Preview")
    st.dataframe(df)
