
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Amazon Order Dashboard", layout="centered")

st.title("Amazon Order Dashboard")

uploaded_file = st.file_uploader("Upload Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Data Preview:", df.head())

    df['order-id'] = df['amazon-order-id'].astype(str)
if 'order-type' in df.columns:
    df['order-type'] = df['order-type'].fillna('')
else:
    df['order-type'] = ''



    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)

    vine_orders = df[df['order-type'] == 'Vine']
    retail_orders = df[df['order-type'] != 'Vine']

    shipped = df[df['item-status'] == 'Shipped']
    pending = df[df['item-status'] == 'Pending']

    st.subheader("Order Summary")
    st.metric("Total Vine Orders (Claimed)", vine_orders['order-id'].nunique())
    st.metric("Shipped Vine Units", vine_orders[vine_orders['item-status'] == 'Shipped']['quantity'].sum())
    st.metric("Retail Orders", retail_orders['order-id'].nunique())
    st.metric("Retail Units (Shipped)", retail_orders[retail_orders['item-status'] == 'Shipped']['quantity'].sum())
    st.metric("Pending Units", pending['quantity'].sum())
    st.metric("Total Shipped Units", shipped['quantity'].sum())
