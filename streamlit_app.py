import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Identify Vine orders
    df["vine"] = df["promotion-ids"].astype(str).str.contains("vine", case=False, na=False)

    # Rename columns to display-friendly names
    df = df.rename(columns={
        "item-status": "status",
        "item-price": "price",
        "item-promotion-discount": "discount",
        "ship-city": "city",
        "ship-state": "state",
        "promotion-ids": "promotion"
    })

    # Calculate metrics
    total_orders = len(df)
    vine_orders = df["vine"].sum()
    retail_orders = total_orders - vine_orders

    shipped_df = df[df["status"] == "Shipped"]
    pending_df = df[df["status"] != "Shipped"]

    shipped_units = shipped_df["quantity"].sum()
    pending_units = pending_df["quantity"].sum()

    shipped_vine_units = shipped_df[shipped_df["vine"] == True]["quantity"].sum()
    shipped_retail_units = shipped_df[shipped_df["vine"] == False]["quantity"].sum()

    pending_orders = pending_df["amazon-order-id"].nunique()
    fba_vine_units_sent = df[df["vine"] == True]["quantity"].sum()

    # Show KPIs
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

    # Display cleaned table with selected columns
    st.markdown("---")
    st.subheader("Full Order Data")
    selected_columns = [
        "amazon-order-id", "purchase-date", "order-status", "ship-service-level",
        "status", "quantity", "price", "discount", "city", "state", "promotion", "vine"
    ]
    st.dataframe(df[selected_columns])
