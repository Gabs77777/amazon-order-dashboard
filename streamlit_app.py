import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Amazon Order Dashboard")

# Upload file
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

# Sidebar manual inputs
fba_vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", min_value=0, value=15)
vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", min_value=0, value=14)

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = [col.lower().strip().replace(' ', '-') for col in df.columns]

    # Basic metrics
    total_orders = len(df)
    retail_orders = df[~df['order-id'].astype(str).str.startswith('V')].shape[0]
    vine_orders = df[df['order-id'].astype(str).str.startswith('V')].shape[0]
    pending_orders = df[df['order-status'].str.lower() == 'pending'].shape[0]

    # Shipped status
    shipped_df = df[df['order-status'].str.lower() == 'shipped']
    shipped_retail_units = shipped_df[~shipped_df['order-id'].astype(str).str.startswith('V')]['quantity'].sum()
    shipped_vine_units = shipped_df[shipped_df['order-id'].astype(str).str.startswith('V')]['quantity'].sum()

    # Total units ordered
    retail_units_ordered = df[~df['order-id'].astype(str).str.startswith('V')]['quantity'].sum()
    vine_units_ordered = vine_orders  # 1 unit per Vine order as confirmed
    total_units = retail_units_ordered + vine_units_ordered

    pending_units = df[df['order-status'].str.lower() == 'pending']['quantity'].sum()

    # Dashboard display
    st.subheader("Untitled spreadsheet.xlsx")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Orders", total_orders)
        st.metric("FBA Vine Units Sent", fba_vine_units_sent)
        st.metric("Shipped Vine Units", shipped_vine_units)

    with col2:
        st.metric("Retail Orders", retail_orders)
        st.metric("Vine Units Enrolled", vine_units_enrolled)
        st.metric("Shipped Retail Units", shipped_retail_units)

    with col3:
        st.metric("Vine Orders", vine_orders)
        st.metric("Vine Units Ordered", vine_units_ordered)
        st.metric("Pending Units", pending_units)

    with col4:
        st.metric("Pending Orders", pending_orders)
        st.metric("Retail Units Ordered", retail_units_ordered)

    st.subheader("Total Units Ordered")
    st.metric("Total Units", total_units)

    st.subheader("Full Order Data")
    st.dataframe(df)
