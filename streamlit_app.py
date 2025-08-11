import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

fba_vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", min_value=0, value=15)
vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", min_value=0, value=14)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Preview raw columns
    st.write("Raw Columns:", df.columns.tolist())

    # Try to normalize and guess column names
    df.columns = [col.lower().strip().replace(" ", "-") for col in df.columns]

    # Handle column detection
    order_id_col = next((col for col in df.columns if "order-id" in col), None)
    quantity_col = next((col for col in df.columns if "quantity" in col), None)
    status_col = next((col for col in df.columns if "status" in col), None)

    if not order_id_col or not quantity_col or not status_col:
        st.error("Required columns not found. Please check your Excel file.")
    else:
        df[order_id_col] = df[order_id_col].astype(str)
        df[quantity_col] = pd.to_numeric(df[quantity_col], errors='coerce').fillna(0)

        # Classify Vine and Retail
        is_vine = df[order_id_col].str.startswith("V")
        is_pending = df[status_col].str.lower() == "pending"
        is_shipped = df[status_col].str.lower() == "shipped"

        vine_orders = df[is_vine]
        retail_orders = df[~is_vine]

        total_orders = len(df)
        total_units = retail_orders[quantity_col].sum() + len(vine_orders)  # 1 unit per Vine order
        pending_orders = df[is_pending].shape[0]
        pending_units = df[is_pending][quantity_col].sum()
        shipped_retail_units = retail_orders[is_shipped][quantity_col].sum()
        shipped_vine_units = vine_orders[is_shipped].shape[0]

        # Show metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Orders", total_orders)
            st.metric("FBA Vine Units Sent", fba_vine_units_sent)
            st.metric("Shipped Vine Units", shipped_vine_units)
        with col2:
            st.metric("Retail Orders", len(retail_orders))
            st.metric("Vine Units Enrolled", vine_units_enrolled)
            st.metric("Shipped Retail Units", shipped_retail_units)
        with col3:
            st.metric("Vine Orders", len(vine_orders))
            st.metric("Vine Units Ordered", len(vine_orders))
            st.metric("Pending Units", pending_units)
        with col4:
            st.metric("Pending Orders", pending_orders)
            st.metric("Retail Units Ordered", retail_orders[quantity_col].sum())

        st.subheader("Total Units Ordered")
        st.metric("Total Units", total_units)

        st.subheader("Full Order Data")
        st.dataframe(df)
