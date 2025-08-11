import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

# User input
fba_vine_units_sent = st.number_input("FBA Vine Units Sent", value=15)
vine_units_enrolled = st.number_input("Vine Units Enrolled", value=14)

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

# Hardcoded Vine Order IDs
VINE_ORDER_IDS = {
    "113-3697505-6920636",
    "113-1335019-9650257",
    "113-5865865-6980823",
    "113-3937476-7462451",
    "113-8219665-0103427",
    "113-5240604-4890656",
    "113-7900491-4126816",
    "113-2237695-8090258"
}

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "-")

    # Standardize column names
    df = df.rename(columns={
        "amazon-order-id": "order_id",
        "order-status": "status",
        "quantity": "qty"
    })

    # Clean values
    df["order_id"] = df["order_id"].astype(str).str.strip()
    df["status"] = df["status"].astype(str).str.lower().str.strip()
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(1)

    # Tag Vine orders
    df["is_vine"] = df["order_id"].isin(VINE_ORDER_IDS)
    df["is_shipped"] = df["status"] == "shipped"
    df["is_pending"] = df["status"] == "pending"

    # Order counts
    total_orders = len(df)
    vine_orders = df["is_vine"].sum()
    retail_orders = total_orders - vine_orders
    pending_orders = df["is_pending"].sum()

    # Unit counts
    vine_units_ordered = df[df["is_vine"]]["qty"].sum()
    retail_units_ordered = df[~df["is_vine"]]["qty"].sum()
    shipped_vine_units = df[df["is_vine"] & df["is_shipped"]]["qty"].sum()
    shipped_retail_units = df[~df["is_vine"] & df["is_shipped"]]["qty"].sum()
    pending_units = df[df["is_pending"]]["qty"].sum()
    total_units = df["qty"].sum()

    # Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", total_orders)
    col2.metric("Retail Orders", retail_orders)
    col3.metric("Vine Orders", vine_orders)
    col4.metric("Pending Orders", pending_orders)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("FBA Vine Units Sent", fba_vine_units_sent)
    col2.metric("Vine Units Enrolled", vine_units_enrolled)
    col3.metric("Vine Units Ordered", int(vine_units_ordered))
    col4.metric("Retail Units Ordered", int(retail_units_ordered))

    col1, col2 = st.columns(2)
    col1.metric("Shipped Vine Units", int(shipped_vine_units))
    col2.metric("Shipped Retail Units", int(shipped_retail_units))

    col1, col2 = st.columns(2)
    col1.metric("Pending Units", int(pending_units))
    col2.metric("Total Units Ordered", int(total_units))

    st.subheader("Full Order Data")
    st.dataframe(df)
