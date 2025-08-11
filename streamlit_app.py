import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")

st.markdown("<h1 style='color:white;'>Amazon Order Dashboard</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Calculations
    total_orders = df['amazon-order-id'].nunique()
    vine_orders = df['promotion-ids'].str.contains('vine.enrollment', na=False).sum()
    retail_orders = total_orders - vine_orders

    shipped_orders = df[df['order-status'] == 'Shipped']
    pending_orders = df[df['order-status'] == 'Pending']

    shipped_units = shipped_orders.shape[0]
    pending_units = pending_orders.shape[0]

    shipped_vine_units = shipped_orders['promotion-ids'].str.contains('vine.enrollment', na=False).sum()
    shipped_retail_units = shipped_units - shipped_vine_units

    # You can edit this manually if needed
    fba_vine_units_sent = 10

    # Layout
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", total_orders)
        st.metric("Retail Orders", retail_orders)
        st.metric("Vine Orders", vine_orders)
    with col2:
        st.metric("FBA Vine Units Sent", fba_vine_units_sent)
        st.metric("Shipped Units", shipped_units)
        st.metric("Pending Units", pending_units)
    with col3:
        st.metric("Shipped Vine Units", shipped_vine_units)
        st.metric("Shipped Retail Units", shipped_retail_units)
        st.metric("Pending Orders", pending_orders.shape[0])

    st.subheader("Full Order Data")
    st.dataframe(df)
