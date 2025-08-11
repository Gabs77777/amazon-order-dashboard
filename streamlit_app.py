import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

# Manual override sidebar
st.sidebar.markdown("### Manual Overrides")
vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", min_value=0, value=15)
vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", min_value=0, value=14)

# Upload file
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Ensure columns are string type for processing
    df["promotion-ids"] = df["promotion-ids"].astype(str).fillna("").str.lower()
    df["order-status"] = df["order-status"].astype(str).str.lower()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)

    # Classify Vine orders: only those with valid vine.enrollment tag
    df["vine_order"] = df["promotion-ids"].str.contains("vine.enrollment", na=False)

    # Subsets
    vine_df = df[df["vine_order"] == True]
    retail_df = df[df["vine_order"] == False]

    # Orders
    total_orders = len(df)
    vine_orders = len(vine_df)
    retail_orders = len(retail_df)
    pending_orders = len(df[df["order-status"] == "pending"])

    # Units
    vine_units_ordered = vine_df["quantity"].sum()
    shipped_vine_units = vine_df[vine_df["order-status"] == "shipped"]["quantity"].sum()

    retail_units_ordered = retail_df["quantity"].sum()
    shipped_retail_units = retail_df[retail_df["order-status"] == "shipped"]["quantity"].sum()

    total_units = vine_units_ordered + retail_units_ordered
    pending_units = df[df["order-status"] == "pending"]["quantity"].sum()

    # Layout
    st.markdown("### Orders")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders", total_orders)
    c2.metric("Retail Orders", retail_orders)
    c3.metric("Vine Orders", vine_orders)
    c4.metric("Pending Orders", pending_orders)

    st.markdown("### Units")
    u1, u2, u3, u4 = st.columns(4)
    u1.metric("FBA Vine Units Sent", vine_units_sent)
    u2.metric("Vine Units Enrolled", vine_units_enrolled)
    u3.metric("Vine Units Ordered", vine_units_ordered)
    u4.metric("Retail Units Ordered", retail_units_ordered)

    u5, u6, u7, u8 = st.columns(4)
    u5.metric("Total Units Ordered", total_units)
    u6.metric("Pending Units", pending_units)
    u7.metric("Shipped Vine Units", shipped_vine_units)
    u8.metric("Shipped Retail Units", shipped_retail_units)

    st.markdown("### Full Order Data")
    st.dataframe(df, use_container_width=True)
