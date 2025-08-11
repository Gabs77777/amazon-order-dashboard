import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    df['order-status'] = df['order-status'].fillna('')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
    df['promotion-ids'] = df['promotion-ids'].fillna('')
    df['amazon-order-id'] = df['amazon-order-id'].astype(str)

    vine_key = 'vine.enrollment.ada9f609-d98f-4e51-845f-f586ae70b3bd'
    df['is_vine_item'] = df['promotion-ids'].str.contains(vine_key)

    # Group by order
    orders = df.groupby('amazon-order-id').agg({
        'is_vine_item': 'max',
        'order-status': lambda x: list(set(x)),
        'quantity': 'sum'
    }).reset_index()

    orders['type'] = orders['is_vine_item'].apply(lambda x: 'Vine' if x else 'Retail')
    orders['shipped'] = orders['order-status'].apply(lambda x: 'Shipped' in x)
    orders['pending'] = orders['order-status'].apply(lambda x: 'Pending' in x)

    # Totals
    total_orders = len(orders)
    vine_orders = len(orders[orders['type'] == 'Vine'])
    retail_orders = len(orders[orders['type'] == 'Retail'])

    shipped_vine_units = df[(df['is_vine_item']) & (df['order-status'] == 'Shipped')]['quantity'].sum()
    shipped_retail_units = df[(~df['is_vine_item']) & (df['order-status'] == 'Shipped')]['quantity'].sum()
    total_shipped_units = shipped_vine_units + shipped_retail_units
    pending_units = df[df['order-status'] == 'Pending']['quantity'].sum()

    # Display
    st.markdown("### Order Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Orders", total_orders)
    c2.metric("Retail Orders", retail_orders)
    c3.metric("Vine Orders", vine_orders)

    st.markdown("### Fulfillment Summary")
    c4, c5, c6, c7 = st.columns(4)
    c4.metric("Total Shipped Units", int(total_shipped_units))
    c5.metric("Shipped Vine Units", int(shipped_vine_units))
    c6.metric("Shipped Retail Units", int(shipped_retail_units))
    c7.metric("Pending Units", int(pending_units))

    st.markdown("### Data Preview")
    st.dataframe(df)

