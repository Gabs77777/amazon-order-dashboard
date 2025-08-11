import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Required columns
    required = ['amazon-order-id', 'order-status', 'quantity', 'promotion-ids']
    if not all(col in df.columns for col in required):
        st.error("Missing required columns: " + ", ".join(col for col in required if col not in df.columns))
        st.stop()

    # Clean and normalize data
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(1).astype(int)
    df['order-status'] = df['order-status'].astype(str).str.lower()
    df['promotion-ids'] = df['promotion-ids'].astype(str).fillna("")

    # Order-level Vine detection
    df['vine_flag'] = df['promotion-ids'].str.contains('vine.enrollment', case=False)
    order_vine_status = df.groupby('amazon-order-id')['vine_flag'].max()
    df['vine_order'] = df['amazon-order-id'].map(order_vine_status)

    # Sidebar overrides
    st.sidebar.header("Manual Overrides")
    vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", value=15)
    vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", value=14)

    # Orders
    orders_df = df[['amazon-order-id', 'order-status', 'vine_order']].drop_duplicates()
    total_orders = len(orders_df)
    vine_orders = orders_df['vine_order'].sum()
    retail_orders = total_orders - vine_orders
    pending_orders = (orders_df['order-status'] == 'pending').sum()

    # Units
    vine_units = df[df['vine_order']]['quantity'].sum()
    retail_units = df[~df['vine_order']]['quantity'].sum()
    total_units = vine_units + retail_units

    pending_units = df[df['order-status'] == 'pending']['quantity'].sum()
    shipped_vine_units = df[(df['vine_order']) & (df['order-status'] == 'shipped')]['quantity'].sum()
    shipped_retail_units = df[(~df['vine_order']) & (df['order-status'] == 'shipped')]['quantity'].sum()

    # Display
    st.markdown("### Orders")
    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Total Orders", total_orders)
    o2.metric("Retail Orders", int(retail_orders))
    o3.metric("Vine Orders", int(vine_orders))
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
    st.dataframe(
        df[['amazon-order-id', 'purchase-date', 'order-status', 'quantity', 'promotion-ids', 'vine_order']],
        use_container_width=True
    )
