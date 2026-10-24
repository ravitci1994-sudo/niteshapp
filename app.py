col1, col2, col3 = st.columns(3)
col1.metric(label="Total Trips", value="348", delta="12 Trips (vs Last Week)")
col2.metric(label="On-Time Delivery", value="202", delta="5.2%", delta_color="normal")
col3.metric(label="Delayed Trips", value="146", delta="-2.1%", delta_color="inverse")
