# Identify Vine orders
df['is_vine'] = df['promotion-ids'].str.contains('vine.enrollment', na=False)

# Order summaries
total_orders = df['amazon-order-id'].nunique()
vine_orders = df[df['is_vine']].shape[0]
retail_orders = total_orders - vine_orders

# Shipped and Pending
shipped = df[df['order-status'] == 'Shipped']
pending = df[df['order-status'] == 'Pending']

shipped_units = shipped.shape[0]
pending_units = pending.shape[0]

# Correct breakdown
shipped_vine_units = shipped[shipped['is_vine']].shape[0]
shipped_retail_units = shipped_units - shipped_vine_units
pending_orders = pending.shape[0]

# Hardcoded FBA vine units sent
fba_vine_units_sent = vine_orders  # or change manually if needed
