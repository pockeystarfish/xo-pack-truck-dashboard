import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt

# Streamlit App: XO PACK Truck Type Recommendation Dashboard
st.set_page_config(page_title="XO PACK Truck Type Recommendation", layout="wide")

# Main title
st.title("📦 XO PACK Truck Type Recommendation Dashboard")

# --- Order Data Input (Sidebar) ---
st.sidebar.header("Order Data Input")
st.sidebar.write("Enter each box's dimensions (cm) and quantity:")
initial_df = pd.DataFrame(columns=["length", "width", "height", "quantity"])
df = st.sidebar.data_editor(initial_df, num_rows="dynamic", use_container_width=True)

# --- Truck Cost Inputs (Sidebar) ---
st.sidebar.header("Truck Costs per Shipment")
cost_20ft = st.sidebar.number_input("20 ft vehicle cost", min_value=0.0, value=150.0, step=10.0, format="%.2f")
cost_24ft = st.sidebar.number_input("24 ft vehicle cost", min_value=0.0, value=200.0, step=10.0, format="%.2f")
cost_32ft = st.sidebar.number_input("32 ft vehicle cost", min_value=0.0, value=300.0, step=10.0, format="%.2f")

# Hard-coded truck capacities (m³)
capacities = {
    "20 ft vehicle": 30.0,
    "24 ft vehicle": 40.0,
    "32 ft vehicle": 60.0,
}
costs = {
    "20 ft vehicle": cost_20ft,
    "24 ft vehicle": cost_24ft,
    "32 ft vehicle": cost_32ft,
}

# Validate and process order data
required_cols = ["length", "width", "height", "quantity"]
if df.empty or not all(col in df.columns for col in required_cols):
    st.warning("Please enter valid order data in all columns.")
else:
    # Convert types and clean
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["quantity"] = df["quantity"].fillna(1)
    df.dropna(subset=required_cols, inplace=True)

    # Calculate volumes
    df["volume_m3"] = (df["length"] * df["width"] * df["height"]) / 1e6
    df["total_volume_m3"] = df["volume_m3"] * df["quantity"]
    total_volume = df["total_volume_m3"].sum()

    # Display summary
    st.subheader("Shipment Summary")
    st.write(f"**Total Shipment Volume:** {total_volume:.2f} m³")

    # Determine max single-type counts
    n20_max = math.ceil(total_volume / capacities["20 ft vehicle"])
    n24_max = math.ceil(total_volume / capacities["24 ft vehicle"])
    n32_max = math.ceil(total_volume / capacities["32 ft vehicle"])

    # Generate feasible combinations
    combos = []
    for n20 in range(n20_max + 1):
        for n24 in range(n24_max + 1):
            for n32 in range(n32_max + 1):
                if n20 + n24 + n32 == 0:
                    continue
                cap_total = (
                    n20 * capacities["20 ft vehicle"] +
                    n24 * capacities["24 ft vehicle"] +
                    n32 * capacities["32 ft vehicle"]
                )
                if cap_total >= total_volume:
                    cost_total = (
                        n20 * costs["20 ft vehicle"] +
                        n24 * costs["24 ft vehicle"] +
                        n32 * costs["32 ft vehicle"]
                    )
                    combos.append({
                        "20 ft": n20,
                        "24 ft": n24,
                        "32 ft": n32,
                        "Total Capacity (m³)": cap_total,
                        "Total Cost": cost_total,
                    })

    # Create DataFrame and identify best plan
    combos_df = pd.DataFrame(combos).sort_values("Total Cost").reset_index(drop=True)
    best_idx = combos_df.index[0]

    # Recommended Plan
    best = combos_df.loc[best_idx]
    st.subheader("Recommended Loading Plan")
    st.write(
        f"**Plan:** {int(best['20 ft'])}×20 ft, {int(best['24 ft'])}×24 ft, {int(best['32 ft'])}×32 ft"
    )
    st.write(f"**Estimated Cost:** {best['Total Cost']:.2f}")

    # Highlighted table of all plans
    st.subheader("All Feasible Plans")
    styled = combos_df.style.apply(
        lambda row: ['background-color: red' if row.name == best_idx else '' for _ in row], axis=1
    )
    st.write(styled)

    # Cost comparison bar chart
    st.subheader("Cost Comparison of Plans")
    fig, ax = plt.subplots()
    colors = ['red' if i == best_idx else 'blue' for i in combos_df.index]
    ax.bar(combos_df.index.astype(str), combos_df["Total Cost"], color=colors)
    ax.set_xlabel("Plan Index (sorted by cost)")
    ax.set_ylabel("Total Cost")
    ax.set_title("Comparison of Loading Plan Costs")
    st.pyplot(fig)

    # Show order details
    st.subheader("Order Details")
    st.dataframe(df.reset_index(drop=True))
