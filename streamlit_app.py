import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")

st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean and prepare data
    df['order-status'] = df.get('order-status', '').fillna('')
    df['quantity'] = pd.to_numeric(df.get('quantity', 0), errors='coerce').fillna(0)
    df['promotion-ids'] = df.get('promotion-ids', '').fillna('')
    df['amazon-order-id'] = df.get('amazon-order-id', '').astype(str)

    vine_key = 'vine.enrollment.ada9f609-d98f-4e51-845f-f586ae70b3bd'
    df['is_vine'] = df['promotion-ids'].str.contains(vine_key)

    # Group by order ID
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

    # Order counts
    total_orders = order_summary['amazon-order-id'].nunique()
    retail_orders = order_summary[order_summary['type'] == 'Retail']['amazon-order-id'].nunique()
    vine_orders = order_summary[order_summary['type'] == 'Vine']['amazon-order-id'].nunique()

    # Unit counts
    shipped = df[df['order-status'].str.lower() == 'shipped']
    shipped_vine_units = shipped[shipped['is_vine']]['quantity'].sum()
    shipped_retail_units = shipped[~shipped['is_vine']]['quantity'].sum()
    total_shipped_units = shipped['quantity'].sum()
    pending_units = df[df['order-status'].str.lower() == 'pending']['quantity'].sum()

    # --- Display Summary ---
    st.markdown("### Order Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", total_orders)
    col2.metric("Retail Orders", retail_orders)
    col3.metric("Vine Orders", vine_orders)

    st.markdown("### Fulfillment Summary")
    col4, col5, col6, col7 = st.columns(4)
    col4.metric("Total Shipped Units", int(total_shipped_units))
    col5.metric("Shipped Vine Units", int(shipped_vine_units))
    col6.metric("Shipped Retail Units", int(shipped_retail_units))
    col7.metric("Pending Units", int(pending_units))

    # Show Data
    st.markdown("### Data Preview")
    st.dataframe(df)
