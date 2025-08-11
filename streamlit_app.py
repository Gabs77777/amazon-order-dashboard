import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")

st.markdown("<h1 style='color:white; font-size:36px;'>Amazon Order Dashboard</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = [col.strip().lower().replace(" ", "-") for col in df.columns]

    # Detect vine orders
    df["is_vine"] = df["promotion-ids"].astype(str).str.contains("vine", case=False)

    # Normalize and clean
    df["item-status"] = df["item-status"].str.strip().str.lower()
    df["order-status"] = df["order-status"].str.strip().str.capitalize()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)

    # Core metrics
    total_orders = len(df)
    vine_orders = df["is_vine"].sum()
    retail_orders = total_orders - vine_orders
    fba_vine_units_sent = df[df["is_vine"]]["quantity"].sum()

    shipped_df = df[df["item-status"] == "shipped"]
    shipped_units = shipped_df["quantity"].sum()
    shipped_vine_units = shipped_df[shipped_df["is_vine"]]["quantity"].sum()
    shipped_retail_units = shipped_units - shipped_vine_units

    pending_df = df[df["order-status"] == "Pending"]
    pending_orders = len(pending_df)
    pending_units = pending_df["quantity"].sum()

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

    # Clean table
    show_columns = [
        "amazon-order-id", "purchase-date", "order-status", "ship-service-level",
        "item-status", "quantity", "item-price", "item-promotion-discount",
        "ship-city", "ship-state", "promotion-ids", "is_vine"
    ]
    renamed_columns = {
        "item-price": "price",
        "item-promotion-discount": "discount",
        "ship-city": "city",
        "ship-state": "state",
        "promotion-ids": "promotion",
        "is_vine": "vine",
        "item-status": "status"
    }

    clean_df = df[show_columns].rename(columns=renamed_columns)

    st.markdown("---")
    st.subheader("Full Order Data")
    st.dataframe(clean_df, use_container_width=True)
