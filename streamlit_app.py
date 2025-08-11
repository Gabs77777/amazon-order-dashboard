import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

fba_vine_units_sent = st.number_input("FBA Vine Units Sent", min_value=0, value=0)
vine_units_enrolled = st.number_input("Vine Units Enrolled", min_value=0, value=0)

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip().str.lower()

        # Map flexible column names
        column_map = {
            "order_id": ["order id", "amazon-order-id", "order-id"],
            "status": ["status", "order status"],
        }

        for target_col, possible_names in column_map.items():
            found = False
            for name in possible_names:
                if name in df.columns:
                    df.rename(columns={name: target_col}, inplace=True)
                    found = True
                    break
            if not found:
                st.error(f"Missing required column: {target_col}")
                st.stop()

        df["order_id"] = df["order_id"].astype(str).str.strip()
        df["status"] = df["status"].astype(str).str.strip().str.lower()

        VINE_ORDER_IDS = {
            "113-4539275-1458601",
            "113-5709703-5945415",
            "113-1234567-1234567"
        }

        df["is_vine"] = df["order_id"].isin(VINE_ORDER_IDS)
        df["is_pending"] = df["status"].str.contains("pending", na=False)

        total_orders = len(df)
        vine_orders = df["is_vine"].sum()
        retail_orders = total_orders - vine_orders
        vine_units_ordered = vine_orders
        retail_units_ordered = retail_orders

        shipped_df = df[~df["is_pending"]]
        shipped_vine_units = shipped_df["is_vine"].sum()
        shipped_retail_units = len(shipped_df) - shipped_vine_units

        pending_orders = df["is_pending"].sum()
        pending_units = pending_orders
        total_units_ordered = total_orders

        # Metrics display
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
        st.error(f"Error: {e}")
