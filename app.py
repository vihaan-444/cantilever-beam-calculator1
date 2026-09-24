import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="Cantilever Beam Calculator",
    page_icon="📐",
    layout="wide"
)

# Title & Team Details
st.title("📐 Cantilever Beam Deflection & Stress Calculator")
st.caption("Mechanical Engineering Web Simulator | Streamlit App Project")

st.markdown("""
---
**Group Details:**
* **Group No:** 02
* **Members:** vihaan gadhia (Enrollment No: 25012250610023), daksh patel (Enrollment No: 24012250610066),priyansh patel (Enrollment No: 25012250610023)
---
""")

# Sidebar Inputs
st.sidebar.header("⚙️ Input Parameters")

# 1. Material Selection
material_data = {
    "Mild Steel": {"E": 210e9, "yield_strength": 250e6},      # E in Pa, Sy in Pa
    "Aluminum":   {"E": 70e9,  "yield_strength": 95e6},
    "Brass":      {"E": 105e9, "yield_strength": 200e6}
}

selected_material = st.sidebar.selectbox("Select Material", list(material_data.keys()))
E = material_data[selected_material]["E"]
sy = material_data[selected_material]["yield_strength"]

# 2. Beam Length & End Load
st.sidebar.subheader("Beam & Loading")
L = st.sidebar.number_input("Beam Length L (m)", min_value=0.1, max_value=10.0, value=2.0, step=0.1)
P_kN = st.sidebar.number_input("End Point Load P (kN)", min_value=0.1, max_value=500.0, value=5.0, step=0.5)
P = P_kN * 1000  # Convert kN to N

# 3. Cross-Section Selection
st.sidebar.subheader("Cross-Section Dimensions")
shape = st.sidebar.selectbox("Cross-Section Shape", ["Solid Rectangle", "Solid Circular", "I-Section"])

I = 0.0
Z = 0.0

if shape == "Solid Rectangle":
    b_mm = st.sidebar.slider("Width b (mm)", 10.0, 300.0, 50.0)
    h_mm = st.sidebar.slider("Height h (mm)", 10.0, 500.0, 100.0)
    b = b_mm / 1000.0
    h = h_mm / 1000.0
    
    I = (b * h**3) / 12.0
    Z = (b * h**2) / 6.0

elif shape == "Solid Circular":
    d_mm = st.sidebar.slider("Diameter d (mm)", 10.0, 300.0, 50.0)
    d = d_mm / 1000.0
    
    I = (np.pi * d**4) / 64.0
    Z = (np.pi * d**3) / 32.0

elif shape == "I-Section":
    B_mm = st.sidebar.slider("Flange Width B (mm)", 20.0, 400.0, 100.0)
    H_mm = st.sidebar.slider("Total Height H (mm)", 20.0, 600.0, 200.0)
    tf_mm = st.sidebar.slider("Flange Thickness tf (mm)", 2.0, 50.0, 10.0)
    tw_mm = st.sidebar.slider("Web Thickness tw (mm)", 2.0, 50.0, 8.0)
    
    # Validation for impossible I-Section dimensions
    if H_mm <= 2 * tf_mm or B_mm <= tw_mm:
        st.error("Validation Error: Invalid I-section dimensions (Height must exceed 2x Flange Thickness).")
        st.stop()
        
    B, H, tf, tw = B_mm/1000, H_mm/1000, tf_mm/1000, tw_mm/1000
    I = (B * H**3 - (B - tw)*(H - 2*tf)**3) / 12.0
    Z = I / (H / 2.0)

# Main Screen Calculations
M_max = P * L                   # N·m
sigma_max = M_max / Z           # Pa
delta_max = (P * L**3) / (3 * E * I)  # m

sigma_max_MPa = sigma_max / 1e6
sy_MPa = sy / 1e6
delta_max_mm = delta_max * 1000

# Results Dashboard
st.header("📊 Engineering Output")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Section Modulus (Z)", f"{Z*1e6:.2f} cm³")
col2.metric("Max Moment (M_max)", f"{M_max/1000:.2f} kN·m")
col3.metric("Max Bending Stress", f"{sigma_max_MPa:.2f} MPa")
col4.metric("Max Deflection", f"{delta_max_mm:.2f} mm")

# Yield Stress Status Banner
if sigma_max > sy:
    st.error(f"🚨 **WARNING: STRESS EXCEEDS YIELD STRENGTH!**\n\nMaximum stress ({sigma_max_MPa:.2f} MPa) exceeds allowable yield strength of {selected_material} ({sy_MPa:.2f} MPa). The beam will undergo permanent plastic deformation.")
else:
    st.success(f"✅ **DESIGN SAFE!**\n\nMaximum bending stress ({sigma_max_MPa:.2f} MPa) is within the yield limit of {selected_material} ({sy_MPa:.2f} MPa).")

st.markdown("---")
st.subheader("📈 Shear Force, Bending Moment & Deflection Diagrams")

# Plotting Curves along the Beam
x = np.linspace(0, L, 200)
shear_force = np.ones_like(x) * P_kN            # constant V = P
bending_moment = P_kN * (L - x)                 # M(x) = P*(L-x) in kN·m
deflection = (P * (x**3 - 3*L*x**2 + 2*L**3)) / (6 * E * I) * 1000  # v(x) in mm

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# 1. Shear Force Diagram
ax1.plot(x, shear_force, color='crimson', lw=2)
ax1.fill_between(x, shear_force, color='crimson', alpha=0.15)
ax1.set_ylabel("Shear Force (kN)")
ax1.set_title("Shear Force Diagram (SFD)")
ax1.grid(True, linestyle="--", alpha=0.6)

# 2. Bending Moment Diagram
ax2.plot(x, bending_moment, color='navy', lw=2)
ax2.fill_between(x, bending_moment, color='navy', alpha=0.15)
ax2.set_ylabel("Moment (kN·m)")
ax2.set_title("Bending Moment Diagram (BMD)")
ax2.grid(True, linestyle="--", alpha=0.6)

# 3. Beam Deflection Profile
ax3.plot(x, -deflection, color='green', lw=2)
ax3.fill_between(x, -deflection, color='green', alpha=0.15)
ax3.set_xlabel("Beam Position x (m)")
ax3.set_ylabel("Deflection (mm)")
ax3.set_title("Beam Elastic Deflection Curve")
ax3.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
st.pyplot(fig)
