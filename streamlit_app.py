import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.markdown("<h1 style='color:white; font-size: 40px;'>Amazon Order Dashboard</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Prep
    df['promotion-ids'] = df['promotion-ids'].astype(str).fillna('')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
    df['order-status'] = df['order-status'].astype(str).fillna('')
    df['amazon-order-id'] = df['amazon-order-id'].astype(str).fillna('')

    # Vine vs Retail
    vine_id = 'vine.enrollment.ada9f609-d98f-4e51-845f-f586ae70b3bd'
    df['is_vine'] = df['promotion-ids'].str.contains(vine_id)
    df['is_retail'] = ~df['is_vine']

    # Unique order count
    total_orders = df['amazon-order-id'].nunique()
    vine_orders = df[df['is_vine']]['amazon-order-id'].nunique()
    retail_orders = df[df['is_retail']]['amazon-order-id'].nunique()

    # Units
    total_units = df['quantity'].sum()
    shipped_units = df[df['order-status'] == 'Shipped']['quantity'].sum()
    pending_units = df[df['order-status'] == 'Pending']['quantity'].sum()

    shipped_vine_units = df[(df['is_vine']) & (df['order-status'] == 'Shipped')]['quantity'].sum()
    shipped_retail_units = df[(df['is_retail']) & (df['order-status'] == 'Shipped')]['quantity'].sum()

    pending_orders = df[df['order-status'] == 'Pending']['amazon-order-id'].nunique()

    # Style cards
    def card(title, value):
        st.markdown(
            f"""
            <div style="background-color:#1e1e1e;padding:20px 30px;border-radius:12px;text-align:center;height:100%;">
                <h3 style="color:#ccc;margin:0;font-size:16px;">{title}</h3>
                <h2 style="color:white;margin:0;font-size:36px;">{value}</h2>
            </div>
            """, unsafe_allow_html=True
        )

    # Dashboard layout
    st.markdown("### Order Overview")
    col1, col2, col3 = st.columns(3)
    with col1: card("Total Orders", total_orders)
    with col2: card("Retail Orders", retail_orders)
    with col3: card("Vine Orders", vine_orders)

    st.markdown("### Fulfillment Summary")
    col4, col5, col6 = st.columns(3)
    with col4: card("Total Units", total_units)
    with col5: card("Shipped Units", shipped_units)
    with col6: card("Pending Units", pending_units)

    st.markdown("### Shipping Breakdown")
    col7, col8, col9 = st.columns(3)
    with col7: card("Shipped Vine Units", shipped_vine_units)
    with col8: card("Shipped Retail Units", shipped_retail_units)
    with col9: card("Pending Orders", pending_orders)

    st.markdown("### Data Preview")
    st.dataframe(df, use_container_width=True)
