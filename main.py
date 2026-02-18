import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 1. DATABASE & ML CONFIG
# ==========================================
FIREBASE_URL = "https://biochamber-52607-default-rtdb.firebaseio.com/"

@st.cache_resource
def train_biomodel():
    # Model remains the same - trained on your parameter names
    np.random.seed(42)
    data = []
    for _ in range(1000):
        t = np.random.uniform(20, 45)
        p = np.random.uniform(4, 9)
        do = np.random.uniform(0, 100)
        od = np.random.uniform(0, 2)
        dist = np.sqrt((t - 37)**2 + ((p - 7)*5)**2) 
        growth = max(0, 1.0 - (dist / 20))
        data.append([t, p, do, od, growth])
    
    df = pd.DataFrame(data, columns=['temperature', 'ph', 'dissolved_oxygen', 'optical_density', 'growth'])
    model = RandomForestRegressor(n_estimators=50)
    model.fit(df[['temperature', 'ph', 'dissolved_oxygen', 'optical_density']], df['growth'])
    return model

ai_model = train_biomodel()

# ==========================================
# 2. STATIC UI (This part NEVER flickers)
# ==========================================
st.set_page_config(page_title="BioChamber LIVE", layout="wide")

st.title("🌿 BioChamber AI Dashboard")
st.caption("Live connection to Firebase Monitoring System")

# Sidebar for targets (Static)
st.sidebar.header("🎯 Target Settings")
target_temp = st.sidebar.number_input("Optimal Temp (°C)", value=37.0)
target_ph = st.sidebar.number_input("Optimal pH", value=7.0)
st.sidebar.divider()
st.sidebar.write("The AI updates the IoT control node every 5 seconds.")

# ==========================================
# 3. DYNAMIC FRAGMENT (Only this part refreshes)
# ==========================================
@st.fragment(run_every=5)  # <--- This is the magic part!
def monitor_live_data():
    try:
        # Fetch from 'live_readings'
        response = requests.get(f"{FIREBASE_URL}/live_readings.json")
        sensor_data = response.json()
        
        if sensor_data:
            t = float(sensor_data.get('temperature', 0))
            p = float(sensor_data.get('ph', 0))
            do = float(sensor_data.get('dissolved_oxygen', 0))
            od = float(sensor_data.get('optical_density', 0))

            # AI Calculation
            features = np.array([[t, p, do, od]])
            growth_eff = ai_model.predict(features)[0]
            
            # Control Logic
            directions = {"temp_instruction": "STABLE", "ph_instruction": "STABLE"}
            if t < target_temp - 0.5: directions["temp_instruction"] = "HEAT_ON"
            elif t > target_temp + 0.5: directions["temp_instruction"] = "COOLING_ON"
            if p < target_ph - 0.2: directions["ph_instruction"] = "ADD_BASE"
            elif p > target_ph + 0.2: directions["ph_instruction"] = "ADD_ACID"
            
            # Push to Firebase
            requests.patch(f"{FIREBASE_URL}/control.json", data=json.dumps(directions))

            # DISPLAY METRICS (Inside the fragment)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Temperature", f"{t} °C", f"{round(t-target_temp, 2)} dev")
            m2.metric("pH", p, f"{round(p-target_ph, 2)} dev")
            m3.metric("Growth Efficiency", f"{round(growth_eff*100, 1)}%")
            m4.metric("OD (Biomass)", od)

            st.divider()
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("🤖 AI Health Report")
                st.progress(float(growth_eff))
                if growth_eff < 0.8:
                    st.warning(f"Deviation Detected. Efficiency reduced to {round(growth_eff*100)}%")
                else:
                    st.success("Growth parameters are within optimal range.")

            with col_b:
                st.subheader("📡 Active IoT Instructions")
                st.info(f"**Thermal Actuator:** {directions['temp_instruction']}")
                st.info(f"**Chemical Pump:** {directions['ph_instruction']}")
                st.caption(f"Last AI update: {time.strftime('%H:%M:%S')}")
        else:
            st.error("Waiting for data in '/live_readings'...")

    except Exception as e:
        st.error(f"Syncing Error: {e}")

# Call the fragment function
monitor_live_data()
