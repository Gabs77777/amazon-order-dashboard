# Clean layout, manual override, compact display
st.markdown("<h1 style='color:white; font-size:36px;'>Amazon Order Dashboard</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Amazon .xlsx file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    vine_id = 'vine.enrollment.ada9f609-d98f-4e51-845f-f586ae70b3bd'
    df['promotion-ids'] = df['promotion-ids'].astype(str)
    df['order-status'] = df['order-status'].fillna('').astype(str)
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
    df['amazon-order-id'] = df['amazon-order-id'].astype(str)

    df['is_vine'] = df['promotion-ids'].str.contains(vine_id)
    df['is_retail'] = ~df['is_vine']
    df['is_shipped'] = df['order-status'] == 'Shipped'
    df['is_pending'] = df['order-status'] == 'Pending'

    total_orders = df['amazon-order-id'].nunique()
    vine_orders = df[df['is_vine']]['amazon-order-id'].nunique()
    retail_orders = df[df['is_retail']]['amazon-order-id'].nunique()
    shipped_units = df[df['is_shipped']]['quantity'].sum()
    pending_units = df[df['is_pending']]['quantity'].sum()
    shipped_vine_units = df[(df['is_shipped']) & (df['is_vine'])]['quantity'].sum()
    shipped_retail_units = df[(df['is_shipped']) & (df['is_retail'])]['quantity'].sum()
    pending_orders = df[df['is_pending']]['amazon-order-id'].nunique()

    # Manual override
    fba_units_sent = st.number_input("Enter total FBA Vine units sent", min_value=0, max_value=1000, value=15)

    # Metric display (2-column layout)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Orders")
        st.markdown(f"- Total Orders: **{total_orders}**")
        st.markdown(f"- Retail Orders: **{retail_orders}**")
        st.markdown(f"- Vine Orders: **{vine_orders}**")
        st.markdown(f"- Pending Orders: **{pending_orders}**")

    with col2:
        st.markdown("#### Units")
        st.markdown(f"- FBA Vine Units Sent: **{fba_units_sent}**")
        st.markdown(f"- Shipped Units: **{shipped_units}**")
        st.markdown(f"- Shipped Vine Units: **{shipped_vine_units}**")
        st.markdown(f"- Shipped Retail Units: **{shipped_retail_units}**")
        st.markdown(f"- Pending Units: **{pending_units}**")

    st.markdown("---")
    st.markdown("#### Full Order Data")
    st.dataframe(df[['amazon-order-id', 'purchase-date', 'order-status', 'quantity', 'product-name']], use_container_width=True)
