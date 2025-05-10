import streamlit as st
import pandas as pd

# Streamlit App: XO PACK Truck Type Recommendation Dashboard
st.set_page_config(page_title="XO PACK Truck Recommendation", layout="wide")

# Main title
st.title("📦 XO PACK Truck Type Recommendation Dashboard")

# --- Vehicle Capacity & Cost Inputs ---
st.sidebar.header("Vehicle Capacities & Costs")
cap_20ft = st.sidebar.number_input(
    "20 ft vehicle max volume (m³)", min_value=0.0, value=30.0, step=1.0
)
cap_24ft = st.sidebar.number_input(
    "24 ft vehicle max volume (m³)", min_value=0.0, value=40.0, step=1.0
)
cap_32ft = st.sidebar.number_input(
    "32 ft vehicle max volume (m³)", min_value=0.0, value=60.0, step=1.0
)
cost_20ft = st.sidebar.number_input(
    "20 ft vehicle cost", min_value=0.0, value=150.0, step=10.0, format="%.2f"
)
cost_24ft = st.sidebar.number_input(
    "24 ft vehicle cost", min_value=0.0, value=200.0, step=10.0, format="%.2f"
)
cost_32ft = st.sidebar.number_input(
    "32 ft vehicle cost", min_value=0.0, value=300.0, step=10.0, format="%.2f"
)

# --- Order Data Input ---
st.subheader("Order Data Input")
st.write("Please enter each box's dimensions (cm) and quantity below:")
initial_df = pd.DataFrame(
    columns=["length", "width", "height", "quantity"]
)
df = st.experimental_data_editor(initial_df, num_rows="dynamic")

# Validate and process order data
required_cols = ["length", "width", "height", "quantity"]
if df.empty or not all(col in df.columns for col in required_cols):
    st.warning("Enter order data in all columns before proceeding.")
else:
    # Convert types and clean
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["quantity"] = df["quantity"].fillna(1)
    df.dropna(subset=required_cols, inplace=True)

    # Calculate volumes
    df["volume_m3"] = (
        df["length"] * df["width"] * df["height"]
    ) / 1e6
    df["total_volume_m3"] = df["volume_m3"] * df["quantity"]
    total_volume = df["total_volume_m3"].sum()

    # Display summary
    st.subheader("Shipment Summary")
    st.write(f"**Total Shipment Volume:** {total_volume:.2f} m³")

    # Recommendation logic
    def recommend_truck(volume):
        if volume <= cap_20ft:
            return "20 ft vehicle", cost_20ft
        elif volume <= cap_24ft:
            return "24 ft vehicle", cost_24ft
        elif volume <= cap_32ft:
            return "32 ft vehicle", cost_32ft
        else:
            return None, 0.0

    recommended, est_cost = recommend_truck(total_volume)
    if recommended:
        st.write(f"**Recommended Vehicle:** {recommended}")
        st.write(f"**Estimated Cost for {recommended}:** {est_cost:.2f}")
    else:
        st.error(
            "Shipment volume exceeds capacity of all available vehicles."
        )

    # Show order details
    st.subheader("Order Details")
    st.dataframe(df.reset_index(drop=True))
