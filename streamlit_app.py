import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="wide")
st.title("Amazon Order Dashboard")

# Manual input fields
vine_units_sent = st.number_input("FBA Vine Units Sent", min_value=0, step=1, value=15)
vine_units_enrolled = st.number_input("Vine Units Enrolled", min_value=0, step=1, value=14)
actual_fba_stock_input = st.number_input("Actual Vine Units in FBA Stock (as shown on Amazon)", min_value=0, step=1, value=1)

# Upload file
uploaded_file = st.file_uploader("Upload your Amazon .xlsx file", type="xlsx")

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.markdown(f"**{uploaded_file.name}**")

    # Normalize columns
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

    if 'order_id' not in df.columns or 'status' not in df.columns:
        st.error("Missing required columns: 'order_id' and 'status'")
    else:
        # Add order type
        VINE_ORDER_IDS = [
            'vine.enrollment.ada95c37-fb10-407a-814e-bf9f7ff9fa48',
            'vine.enrollment.610c181a-df18-4896-9506-b7bda2193d46',
            'vine.enrollment.6c6b1fe1-3e4c-4a06-bfb0-9b76e82d9a0e',
            'vine.enrollment.8b6b2a0f-9876-4f29-b5be-0e3b3aa25f84'
        ]
        df['order_type'] = df['promotion_ids'].apply(
            lambda x: 'Vine' if isinstance(x, str) and any(code in x for code in VINE_ORDER_IDS) else 'Retail'
        )

        # Parse units and shipped status
        df['quantity'] = pd.to_numeric(df.get('quantity', 1), errors='coerce').fillna(1).astype(int)
        df['shipped'] = df['status'].str.lower().str.contains("shipped")

        # Summary counts
        total_orders = len(df)
        retail_orders = df[df['order_type'] == 'Retail']['order_id'].nunique()
        vine_orders = df[df['order_type'] == 'Vine']['order_id'].nunique()
        pending_orders = df[df['status'].str.lower() == 'pending']['order_id'].nunique()
        vine_units_ordered = df[df['order_type'] == 'Vine']['quantity'].sum()
        retail_units_ordered = df[df['order_type'] == 'Retail']['quantity'].sum()
        shipped_vine_units = df[(df['order_type'] == 'Vine') & (df['shipped'])]['quantity'].sum()
        shipped_retail_units = df[(df['order_type'] == 'Retail') & (df['shipped'])]['quantity'].sum()
        pending_units = df[~df['shipped']]['quantity'].sum()
        remaining_vine_units = actual_fba_stock_input

        # Dashboard
        cols = st.columns(4)
        cols[0].metric("Total Orders", total_orders)
        cols[1].metric("Retail Orders", retail_orders)
        cols[2].metric("Vine Orders", vine_orders)
        cols[3].metric("Pending Orders", pending_orders)

        cols = st.columns(4)
        cols[0].metric("FBA Vine Units Sent", vine_units_sent)
        cols[1].metric("Vine Units Enrolled", vine_units_enrolled)
        cols[2].metric("Vine Units Ordered", vine_units_ordered)
        cols[3].metric("Retail Units Ordered", retail_units_ordered)

        cols = st.columns(3)
        cols[0].metric("Shipped Vine Units", shipped_vine_units)
        cols[1].metric("Shipped Retail Units", shipped_retail_units)
        cols[2].metric("Pending Units", pending_units)

        st.markdown("### Remaining Vine Units in Stock")
        st.metric("Remaining Vine Units", remaining_vine_units)

        st.markdown("### Full Order Data")
        st.dataframe(df)
