import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Amazon Order Dashboard")

# Manual override sliders
fba_vine_units_sent = st.sidebar.number_input("FBA Vine Units Sent", min_value=0, value=15)
vine_units_enrolled = st.sidebar.number_input("Vine Units Enrolled", min_value=0, value=14)

uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean up column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "-")

    # Detect Vine orders robustly
    def is_vine(x):
        if pd.isna(x):
            return False
        if isinstance(x, str) and "vine.enrollment" in x.lower():
            return True
        return False

    df["vine_order"] = df["promotion-ids"].apply(is_vine)

    # Separate orders
    vine_df = df[df["vine_order"]]
    retail_df = df[~df["vine_order"]]

    # Basic counts
    total_orders = len(df)
    retail_orders = len(retail_df)
    vine_orders = len(vine_df)
    pending_orders = len(df[df["order-status"].str.lower() == "pending"])

    # Units
    vine_units_ordered = vine_df["quantity"].sum()
    retail_units_ordered = retail_df["quantity"].sum()
    total_units_ordered = vine_units_ordered + retail_units_ordered
    shipped_vine_units = len(vine_df[vine_df["order-status"].str.lower() == "shipped"])
    shipped_retail_units = len(retail_df[retail_df["order-status"].str.lower() == "shipped"])
    pending_units = df[df["order-status"].str.lower() == "pending"]["quantity"].sum()

    # Dashboard
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("Total Orders")
        st.write(total_orders)
    with col2:
        st.subheader("Retail Orders")
        st.write(retail_orders)
    with col3:
        st.subheader("Vine Orders")
        st.write(vine_orders)
    with col4:
        st.subheader("Pending Orders")
        st.write(pending_orders)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.subheader("FBA Vine Units Sent")
        st.write(fba_vine_units_sent)
    with col6:
        st.subheader("Vine Units Enrolled")
        st.write(vine_units_enrolled)
    with col7:
        st.subheader("Vine Units Ordered")
        st.write(vine_units_ordered)
    with col8:
        st.subheader("Retail Units Ordered")
        st.write(retail_units_ordered)

    col9, col10, col11 = st.columns(3)
    with col9:
        st.subheader("Shipped Vine Units")
        st.write(shipped_vine_units)
    with col10:
        st.subheader("Shipped Retail Units")
        st.write(shipped_retail_units)
    with col11:
        st.subheader("Pending Units")
        st.write(pending_units)

    st.subheader("Total Units Ordered")
    st.write(total_units_ordered)

    st.subheader("Full Order Data")
    st.dataframe(df)
