import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    required = ['amazon-order-id', 'order-status', 'quantity', 'promotion-ids']
    if not all(col in df.columns for col in required):
        st.error("Missing required columns.")
        st.stop()

    # Clean up
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
    df['order-status'] = df['order-status'].astype(str).str.lower()
    df['promotion-ids'] = df['promotion-ids'].astype(str)

    # Create order-level vine status
    vine_orders = df[df['promotion-ids'].str.contains('vine.enrollment', case=False, na=False)]
    vine_order_ids = vine_orders['amazon-order-id'].unique()
    order_vine_map = pd.DataFrame({'amazon-order-id': vine_order_ids, 'vine_order': True})

    # Add vine_order flag to original df
    df = df.merge(order_vine_map, on='amazon-order-id', how='left')
    df['vine_order'] = df['vine_order'].fillna(False)

    # Manual override
    st.sidebar.header("Manual Overrides")
    vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", value=15)
    vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", value=14)

    # Group by order ID for order-level calculations
    order_group = df.groupby('amazon-order-id').agg({
        'order-status': 'first',
        'vine_order': 'max'
    }).reset_index()

    # Orders
    total_orders = len(order_group)
    vine_orders_count = order_group['vine_order'].sum()
    retail_orders = total_orders - vine_orders_count
    pending_orders = (order_group['order-status'] == 'pending').sum()

    # Units
    total_units = df['quantity'].sum()
    vine_units = df[df['vine_order']]['quantity'].sum()
    retail_units = df[~df['vine_order']]['quantity'].sum()
    pending_units = df[df['order-status'] == 'pending']['quantity'].sum()
    shipped_vine_units = df[(df['vine_order']) & (df['order-status'] == 'shipped')]['quantity'].sum()
    shipped_retail_units = df[(~df['vine_order']) & (df['order-status'] == 'shipped')]['quantity'].sum()

    # Layout
    st.markdown("### Orders")
    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Total Orders", total_orders)
    o2.metric("Retail Orders", int(retail_orders))
    o3.metric("Vine Orders", int(vine_orders_count))
    o4.metric("Pending Orders", pending_orders)

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

    st.markdown("### Full Order Data")
    st.dataframe(df[['amazon-order-id', 'purchase-date', 'order-status', 'quantity', 'promotion-ids', 'vine_order']], use_container_width=True)
