import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")

st.title("Amazon Order Dashboard")

# Manual inputs
fba_vine_units_sent = st.number_input("FBA Vine Units Sent", min_value=0, value=0)
vine_units_enrolled = st.number_input("Vine Units Enrolled", min_value=0, value=0)

# File uploader
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()

        # Expected columns (normalize)
        expected_columns = [
            "order id", "merchant-order id", "purchase date", "last updated date",
            "status", "fulfillment channel", "sales channel", "order channel", "url",
            "ship-service-level", "product-name"
        ]

        # Rename columns for consistency
        df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]

        # Check and clean required columns
        required_columns = ["order_id", "status"]
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Missing required column: {col}")
                st.stop()

        df["order_id"] = df["order_id"].astype(str).str.strip()
        df["status"] = df["status"].astype(str).str.strip().str.lower()

        # Hardcoded Vine order IDs (change if needed)
        VINE_ORDER_IDS = {
            "113-4539275-1458601",
            "113-5709703-5945415",
            "113-1234567-1234567"  # example placeholder
        }

        df["is_vine"] = df["order_id"].isin(VINE_ORDER_IDS)
        df["is_pending"] = df["status"].str.contains("pending", na=False)

        total_orders = len(df)
        vine_orders = df["is_vine"].sum()
        retail_orders = total_orders - vine_orders

        vine_units_ordered = vine_orders  # Each Vine order is 1 unit
        retail_units_ordered = total_orders - vine_orders

        shipped_df = df[~df["is_pending"]]
        shipped_vine_units = shipped_df["is_vine"].sum()
        shipped_retail_units = len(shipped_df) - shipped_vine_units

        pending_orders = df["is_pending"].sum()
        pending_units = pending_orders

        total_units_ordered = total_orders

        # Display metrics
        st.markdown("###")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Orders", total_orders)
        col2.metric("Retail Orders", retail_orders)
        col3.metric("Vine Orders", vine_orders)
        col4.metric("Pending Orders", pending_orders)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("FBA Vine Units Sent", fba_vine_units_sent)
        col2.metric("Vine Units Enrolled", vine_units_enrolled)
        col3.metric("Vine Units Ordered", vine_units_ordered)
        col4.metric("Retail Units Ordered", retail_units_ordered)

        col1, col2, col3 = st.columns(3)
        col1.metric("Shipped Vine Units", shipped_vine_units)
        col2.metric("Shipped Retail Units", shipped_retail_units)
        col3.metric("Pending Units", pending_units)

        st.metric("Total Units Ordered", total_units_ordered)

        st.subheader("Full Order Data")
        st.dataframe(df)

    except Exception as e:
        st.error(f"Failed to process file: {e}")
