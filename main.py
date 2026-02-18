import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 1. DATABASE & ML CONFIGURATION
# ==========================================
FIREBASE_URL = "https://biochamber-52607-default-rtdb.firebaseio.com/"

@st.cache_resource
def train_control_model():
    # Model learns the "Efficiency Landscape"
    np.random.seed(42)
    X, y = [], []
    for _ in range(1200):
        t = np.random.uniform(15, 50); p = np.random.uniform(3, 10)
        do = np.random.uniform(0, 100); od = np.random.uniform(0, 5)
        # Efficiency Logic (E.coli targets: 37C, 7pH, 40DO)
        eff = np.exp(-((t-37)**2)/50) * np.exp(-((p-7)**2)/2) * np.exp(-((do-40)**2)/1000)
        X.append([t, p, do, od]); y.append(eff)
    
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    return model

ai_brain = train_control_model()

# ==========================================
# 2. UI LAYOUT & SETTINGS
# ==========================================
st.set_page_config(page_title="BioChamber AI", layout="wide")
st.title("🧪 BioChamber: Microbial Intelligence System")

# Sidebar: Selection of Microbe Profile
st.sidebar.header("Microbe Profile")
microbe = st.sidebar.selectbox("Current Microorganism", ["E. coli", "S. cerevisiae (Yeast)", "Custom"])

if microbe == "E. coli":
    ideal_t, ideal_p, ideal_do = 37.0, 7.0, 40.0
elif microbe == "S. cerevisiae (Yeast)":
    ideal_t, ideal_p, ideal_do = 30.0, 5.0, 20.0
else:
    ideal_t = st.sidebar.number_input("Custom Ideal Temp", value=37.0)
    ideal_p = st.sidebar.number_input("Custom Ideal pH", value=7.0)
    ideal_do = st.sidebar.number_input("Custom Ideal DO (%)", value=40.0)

# ==========================================
# 3. DYNAMIC MONITORING & MAINTENANCE
# ==========================================
@st.fragment(run_every=5)
def process_bioreactor():
    try:
        response = requests.get(f"{FIREBASE_URL}/live_readings.json")
        data = response.json()
        
        if data:
            # SENSOR DATA
            cur_t = float(data.get('temperature', 0))
            cur_p = float(data.get('ph', 0))
            cur_do = float(data.get('dissolved_oxygen', 0))
            cur_od = float(data.get('optical_density', 0))

            # AI CALCULATION
            efficiency = ai_brain.predict(np.array([[cur_t, cur_p, cur_do, cur_od]]))[0]

            # NUMERICAL DEVIATION CALCULATION
            diff_t = round(ideal_t - cur_t, 2)
            diff_p = round(ideal_p - cur_p, 2)
            diff_do = round(ideal_do - cur_do, 2)

            # CONTROL DIRECTIVES
            actions = {"thermal": "STABLE", "ph_pump": "STABLE", "oxygen_flow": "STABLE"}
            if diff_t > 0.5: actions["thermal"] = "HEAT_ON"
            elif diff_t < -0.5: actions["thermal"] = "COOLING_ON"
            
            if diff_p > 0.1: actions["ph_pump"] = "ADD_BASE"
            elif diff_p < -0.1: actions["ph_pump"] = "ADD_ACID"
            
            if diff_do > 5: actions["oxygen_flow"] = "INCREASE_AERATION"
            elif diff_do < -5: actions["oxygen_flow"] = "DECREASE_AERATION"

            # FIREBASE UPDATE
            requests.patch(f"{FIREBASE_URL}/control.json", data=json.dumps({
                "commands": actions, "growth_efficiency": round(efficiency, 3), "timestamp": time.strftime("%H:%M:%S")
            }))

            # --- SECTION 1: ACTIVE SENSOR DATA ---
            st.subheader("📊 Section 1: Live Sensor Readings")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Temperature", f"{cur_t}°C")
            c2.metric("pH Level", f"{cur_p}")
            c3.metric("Dissolved Oxygen", f"{cur_do}%")
            c4.metric("Optical Density", f"{cur_od}")
            
            # --- SECTION 2: AI MAINTENANCE DATA ---
            st.divider()
            st.subheader("🤖 Section 2: AI Maintenance & Ideal Optimization")
            
            # Numerical Maintenance Table
            maintenance_data = {
                "Parameter": ["Temperature (°C)", "pH Level", "Dissolved Oxygen (%)"],
                "Live Value": [cur_t, cur_p, cur_do],
                "ML Ideal Target": [ideal_t, ideal_p, ideal_do],
                "Numerical Correction Needed": [diff_t, diff_p, diff_do],
                "AI IoT Directive": [actions['thermal'], actions['ph_pump'], actions['oxygen_flow']]
            }
            df_maint = pd.DataFrame(maintenance_data)
            
            # Apply color styling to the "Correction Needed" column
            def color_diff(val):
                color = 'red' if abs(val) > 0.5 else 'green'
                return f'color: {color}'
            
            st.table(df_maint)

            # Health Visuals
            st.write(f"**Growth System Efficiency:** {round(efficiency * 100, 1)}%")
            st.progress(float(efficiency))
            st.caption(f"Last AI Calculation: {time.strftime('%H:%M:%S')}")

        else:
            st.error("⚠️ Error: '/live_readings' node is empty in Firebase.")

    except Exception as e:
        st.error(f"System Error: {e}")

process_bioreactor()
