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

    vine_orders = order_summary[order_summary['type'] == 'Vine']
    retail_orders = order_summary[order_summary['type'] == 'Retail']
    shipped_vine = vine_orders[vine_orders['shipped']]
    shipped_retail = retail_orders[retail_orders['shipped']]

    total_shipped_units = df[df['order-status'] == 'Shipped']['quantity'].sum()
    shipped_vine_units = df[(df['order-status'] == 'Shipped') & (df['is_vine'])]['quantity'].sum()
    shipped_retail_units = df[(df['order-status'] == 'Shipped') & (~df['is_vine'])]['quantity'].sum()
    pending_units = df[df['order-status'] == 'Pending']['quantity'].sum()

    # Better layout
    st.markdown("### Order Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", order_summary['amazon-order-id'].nunique())
    col2.metric("Retail Orders", retail_orders['amazon-order-id'].nunique())
    col3.metric("Vine Orders", vine_orders['amazon-order-id'].nunique())

    st.markdown("### Fulfillment Summary")
    col4, col5, col6, col7 = st.columns(4)
    col4.metric("Total Shipped Units", int(total_shipped_units))
    col5.metric("Shipped Vine Units", int(shipped_vine_units))
    col6.metric("Shipped Retail Units", int(shipped_retail_units))
    col7.metric("Pending Units", int(pending_units))

    st.markdown("### Data Preview")
    st.dataframe(df)
