import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Identify Vine orders
    df['is_vine'] = df['promotion-ids'].astype(str).str.contains('vine.enrollment', na=False)

    # Shipped and pending
    shipped_df = df[df['order-status'] == 'Shipped']
    pending_df = df[df['order-status'] == 'Pending']

    # Totals
    total_orders = df['amazon-order-id'].nunique()
    vine_orders = df[df['is_vine']]['amazon-order-id'].nunique()
    retail_orders = total_orders - vine_orders

    shipped_units = shipped_df.shape[0]
    pending_units = pending_df.shape[0]
    pending_orders = pending_df['amazon-order-id'].nunique()

    shipped_vine_units = shipped_df[shipped_df['is_vine']].shape[0]
    shipped_retail_units = shipped_units - shipped_vine_units

    # Manual override for FBA Vine units sent
    fba_vine_units_sent = st.number_input("Enter how many Vine units you sent to FBA", min_value=0, value=vine_orders)

    # Display metrics
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
        st.metric("Pending Orders", pending_orders)

    st.markdown("---")
    st.subheader("Full Order Data")
    st.dataframe(df)
