import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="centered")
st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Data Preview:", df.head())

    # Fill blanks to avoid errors
    df['item-status'] = df.get('item-status', '').fillna('')
    df['quantity'] = pd.to_numeric(df.get('quantity', 0), errors='coerce').fillna(0)
    df['promotion-ids'] = df.get('promotion-ids', '').fillna('')

    # Detect Vine orders
    vine_string = 'vine.enrollment.ada9f609-d98f-4e51-845f-f586ae70b3bd'
    df['is_vine'] = df['promotion-ids'].astype(str).str.contains(vine_string)

    # Metrics
    vine_orders = df[df['is_vine']]
    retail_orders = df[~df['is_vine']]

    shipped = df[df['item-status'] == 'Shipped']
    pending = df[df['item-status'] == 'Pending']

    shipped_vine = vine_orders[vine_orders['item-status'] == 'Shipped']
    shipped_retail = retail_orders[retail_orders['item-status'] == 'Shipped']

    # Layout
    st.subheader("Order Summary")
    st.metric("Total Orders", len(df))
    st.metric("Retail Orders", retail_orders['amazon-order-id'].nunique())
    st.metric("Vine Orders", vine_orders['amazon-order-id'].nunique())

    st.subheader("Fulfillment Summary")
    st.metric("Total Shipped Units", shipped['quantity'].sum())
    st.metric("Shipped Vine Units", shipped_vine['quantity'].sum())
    st.metric("Shipped Retail Units", shipped_retail['quantity'].sum())
    st.metric("Pending Units", pending['quantity'].sum())
