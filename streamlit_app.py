import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Detect Vine orders
    df["is_vine"] = df["promotion-ids"].astype(str).str.contains("vine", case=False, na=False)

    # Calculate metrics
    total_orders = len(df)
    vine_orders = df["is_vine"].sum()
    retail_orders = total_orders - vine_orders

    shipped = df[df["item-status"] == "Shipped"]
    pending = df[df["item-status"] != "Shipped"]

    shipped_vine_units = shipped["is_vine"].sum()
    shipped_retail_units = len(shipped) - shipped_vine_units
    shipped_units = len(shipped)

    pending_units = len(pending)
    pending_orders = pending["amazon-order-id"].nunique()

    # Assume Vine Orders = FBA Vine Units Sent (you can override this if needed)
    fba_vine_units_sent = vine_orders

    # Display summary
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

    # Hide unused columns
    columns_to_hide = [
        'merchant-order-id', 'last-updated-date', 'sales-channel', 'order-channel',
        'url', 'sku', 'asin', 'currency', 'item-tax', 'shipping-price',
        'shipping-tax', 'gift-wrap-price', 'gift-wrap-tax', 'ship-promotion-discount',
        'ship-postal-code', 'ship-country', 'is-business-order', 'purchase-order-number',
        'price-designation', 'signature-confirmation-recommended', 'buyer-identification-number',
        'buyer-identification-type'
    ]
    df = df.drop(columns=columns_to_hide, errors='ignore')

    df = df.rename(columns={
        "item-status": "status",
        "item-price": "price",
        "item-promotion-discount": "discount",
        "ship-city": "city",
        "ship-state": "state",
        "promotion-ids": "promotion",
        "is_vine": "vine"
    })

    st.markdown("---")
    st.subheader("Full Order Data")
    st.dataframe(df)
