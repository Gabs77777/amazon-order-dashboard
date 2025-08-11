import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.markdown("<h1 style='color:white; font-size:36px;'>Amazon Order Dashboard</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "-")

    # Make sure quantity column is numeric
    if 'quantity' in df.columns:
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
    else:
        df['quantity'] = 0

    # Identify vine orders by checking if "vine" is in the promotion column
    if 'promotion' in df.columns:
        df['vine'] = df['promotion'].astype(str).str.contains("vine", case=False, na=False)
    else:
        df['vine'] = False

    # Normalize status/order-status
    if 'status' not in df.columns:
        df['status'] = ''
    if 'order-status' not in df.columns:
        df['order-status'] = ''

    # Metrics
    total_orders = len(df)
    vine_orders = df['vine'].sum()
    retail_orders = total_orders - vine_orders

    shipped_units = df[df['status'].str.lower() == 'shipped']['quantity'].sum()
    pending_units = df[df['status'].str.lower() == 'unshipped']['quantity'].sum()
    pending_orders = len(df[df['order-status'].str.lower() == 'pending'])

    shipped_vine_units = df[(df['status'].str.lower() == 'shipped') & (df['vine'])]['quantity'].sum()
    shipped_retail_units = df[(df['status'].str.lower() == 'shipped') & (~df['vine'])]['quantity'].sum()

    fba_vine_units_sent = df[df['vine']]['quantity'].sum()

    # Display
    col1, col2, col3, col4 = st.columns(4)
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
    with col4:
        st.metric("Pending Orders", pending_orders)

    st.markdown("### Full Order Data")
    st.dataframe(df)
