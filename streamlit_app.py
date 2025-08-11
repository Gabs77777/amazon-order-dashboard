import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")

st.title("Amazon Order Dashboard")

# Manual overrides
st.sidebar.markdown("### Manual Overrides")
fba_vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", min_value=0, value=15)
vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", min_value=0, value=14)

# Upload file
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Fill null promotion-ids for classification
    df["promotion-ids"] = df["promotion-ids"].astype(str).fillna("").str.lower()

    # Add vine_order column based on 'promotion-ids' containing "vine.enrollment"
    df["vine_order"] = df["promotion-ids"].str.contains("vine.enrollment", na=False)

    # Classify orders
    vine_orders_df = df[df["vine_order"] == True]
    retail_orders_df = df[df["vine_order"] == False & df["promotion-ids"].notna() & (df["promotion-ids"] != "nan")]

    # Order counts
    total_orders = len(df)
    vine_orders = len(vine_orders_df)
    retail_orders = len(retail_orders_df)
    pending_orders = len(df[df["order-status"].str.lower() == "pending"])

    # Unit counts
    vine_units_ordered = vine_orders_df["quantity"].sum()
    shipped_vine_units = vine_orders_df[df["order-status"].str.lower() == "shipped"]["quantity"].sum()

    retail_units_ordered = retail_orders_df["quantity"].sum()
    shipped_retail_units = retail_orders_df[retail_orders_df["order-status"].str.lower() == "shipped"]["quantity"].sum()

    total_units = df["quantity"].sum()
    pending_units = df[df["order-status"].str.lower() == "pending"]["quantity"].sum()

    # Layout
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", total_orders)
    col2.metric("Retail Orders", retail_orders)
    col3.metric("Vine Orders", vine_orders)
    col4.metric("Pending Orders", pending_orders)

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("FBA Vine Units Sent", fba_vine_units_sent)
    col6.metric("Vine Units Enrolled", vine_units_enrolled)
    col7.metric("Vine Units Ordered", int(vine_units_ordered))
    col8.metric("Shipped Vine Units", int(shipped_vine_units))

    col9, col10, col11, col12 = st.columns(4)
    col9.metric("Retail Units Ordered", int(retail_units_ordered))
    col10.metric("Shipped Retail Units", int(shipped_retail_units))
    col11.metric("Total Units Ordered", int(total_units))
    col12.metric("Pending Units", int(pending_units))

    st.markdown("### Full Order Data")
    st.dataframe(df)

