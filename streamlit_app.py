import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Amazon Orders", layout="wide")
st.markdown("<h1 style='color:white; font-size: 38px;'>Amazon Order Dashboard</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize
    vine_id = 'vine.enrollment.ada9f609-d98f-4e51-845f-f586ae70b3bd'
    df['promotion-ids'] = df['promotion-ids'].astype(str)
    df['order-status'] = df['order-status'].fillna('').astype(str)
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
    df['amazon-order-id'] = df['amazon-order-id'].astype(str)

    # Flags
    df['is_vine'] = df['promotion-ids'].str.contains(vine_id)
    df['is_retail'] = ~df['is_vine']
    df['is_shipped'] = df['order-status'] == 'Shipped'
    df['is_pending'] = df['order-status'] == 'Pending'

    # Metrics
    total_orders = df['amazon-order-id'].nunique()
    vine_orders = df[df['is_vine']]['amazon-order-id'].nunique()
    retail_orders = df[df['is_retail']]['amazon-order-id'].nunique()

    total_fba_units_sent = df[df['is_vine']]['quantity'].sum()

    shipped_units = df[df['is_shipped']]['quantity'].sum()
    pending_units = df[df['is_pending']]['quantity'].sum()
    shipped_vine_units = df[(df['is_shipped']) & (df['is_vine'])]['quantity'].sum()
    shipped_retail_units = df[(df['is_shipped']) & (df['is_retail'])]['quantity'].sum()
    pending_orders = df[df['is_pending']]['amazon-order-id'].nunique()

    # Inline metrics
    def metric(label, value):
        st.markdown(f"""
        <div style="padding:10px 20px;border-radius:8px;background:#111;margin-bottom:10px">
            <p style="color:#999;font-size:14px;margin:0">{label}</p>
            <p style="color:#fff;font-size:26px;margin:0">{value}</p>
        </div>
        """, unsafe_allow_html=True)

    # Layout
    col1, col2, col3 = st.columns(3)
    with col1:
        metric("Total Orders", total_orders)
        metric("Retail Orders", retail_orders)
        metric("Vine Orders", vine_orders)
    with col2:
        metric("FBA Vine Units Sent", total_fba_units_sent)
        metric("Shipped Units", shipped_units)
        metric("Pending Units", pending_units)
    with col3:
        metric("Shipped Vine Units", shipped_vine_units)
        metric("Shipped Retail Units", shipped_retail_units)
        metric("Pending Orders", pending_orders)

    st.markdown("---")
    st.markdown("### Full Order Data")
    st.dataframe(df, use_container_width=True)
