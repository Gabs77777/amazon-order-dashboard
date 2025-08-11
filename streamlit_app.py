import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Data Preview:", df.head())

    # Sanitize columns
    df['item-status'] = df.get('item-status', '').fillna('')
    df['quantity'] = pd.to_numeric(df.get('quantity', 0), errors='coerce').fillna(0)
    df['promotion-ids'] = df.get('promotion-ids', '').fillna('')
    df['amazon-order-id'] = df.get('amazon-order-id', '').astype(str)

    # Vine order detection
    vine_key = 'vine.enrollment.ada9f609-d98f-4e51-845f-f586ae70b3bd'
    df['is_vine'] = df['promotion-ids'].astype(str).str.contains(vine_key)

    # Order-level grouping
    order_groups = df.groupby('amazon-order-id').agg({
        'is_vine': 'max',
        'quantity': 'sum',
        'item-status': lambda x: list(x)
    }).reset_index()

    # Classify order types
    order_groups['type'] = order_groups['is_vine'].apply(lambda x: 'Vine' if x else 'Retail')
    order_groups['shipped'] = order_groups['item-status'].apply(lambda s: 'Shipped' in s)
    order_groups['pending'] = order_groups['item-status'].apply(lambda s: 'Pending' in s)

    # Summary numbers
    total_orders = len(order_groups)
    vine_orders = order_groups[order_groups['type'] == 'Vine']
    retail_orders = order_groups[order_groups['type'] == 'Retail']

    shipped_vine = vine_orders[vine_orders['shipped']]
    shipped_retail = retail_orders[retail_orders['shipped']]

    total_units_shipped = df[df['item-status'] == 'Shipped']['quantity'].sum()
    total_pending_units = df[df['item-status'] == 'Pending']['quantity'].sum()

    # Layout
    st.subheader("Order Summary")
    cols = st.columns(3)
    cols[0].metric("Total Orders", total_orders)
    cols[1].metric("Retail Orders", len(retail_orders))
    cols[2].metric("Vine Orders", len(vine_orders))

    st.subheader("Fulfillment Summary")
    cols = st.columns(4)
    cols[0].metric("Total Shipped Units", total_units_shipped)
    cols[1].metric("Shipped Vine Units", shipped_vine['quantity'].sum())
    cols[2].metric("Shipped Retail Units", shipped_retail['quantity'].sum())
    cols[3].metric("Pending Units", total_pending_units)
