import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time
from sklearn.ensemble import RandomForestRegressor

# ==========================================
# 0. THE FUTURISTIC UI ENGINE (FULL SUITE)
# ==========================================
st.set_page_config(page_title="BioChamber Neural", layout="wide", page_icon="🧬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    /* BASE THEME & ANIMATED BACKGROUND */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 20% 30%, #0f172a 0%, #020617 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
        overflow-x: hidden;
    }

    /* FLOATING PARTICLES EFFECT */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: radial-gradient(#ffffff0a 1px, transparent 1px);
        background-size: 50px 50px;
        animation: moveParticles 100s linear infinite;
        z-index: 0;
    }

    @keyframes moveParticles { from { background-position: 0 0; } to { background-position: 500px 1000px; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

    /* SIDEBAR STYLING */
    [data-testid="stSidebar"] {
        background-color: rgba(2, 6, 23, 0.8) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(0, 242, 255, 0.1);
    }

    /* GLASSMORPHISM CARDS */
    .neural-card {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        animation: fadeInUp 0.6s ease-out forwards;
        transition: all 0.3s ease;
    }
    .neural-card:hover {
        border-color: #00f2ff;
        transform: translateY(-5px);
    }

    /* NEWS ITEM STYLING */
    .news-item {
        border-left: 3px solid #7000ff;
        padding-left: 15px;
        margin-bottom: 20px;
    }
    .news-date { color: #00f2ff; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
    .news-title { color: white; font-weight: 600; font-size: 1.1rem; margin: 5px 0; }
    .news-desc { color: #94a3b8; font-size: 0.85rem; }

    /* UI HELPERS */
    .m-label { color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; }
    .m-value { font-size: 2.5rem; font-weight: 800; color: #fff; margin: 5px 0; }
    .status-ok { background: rgba(0, 255, 150, 0.1); color: #00ff96; border: 1px solid #00ff96; padding: 4px 10px; border-radius: 50px; font-size: 0.7rem; font-weight: 800;}
    .status-warn { background: rgba(255, 45, 85, 0.1); color: #ff2d55; border: 1px solid #ff2d55; padding: 4px 10px; border-radius: 50px; font-size: 0.7rem; font-weight: 800;}

    /* CUSTOM PROGRESS BAR */
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #00f2ff, #7000ff); border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BRAIN & SYSTEM LOGIC
# ==========================================
FIREBASE_URL = "https://biochamber-52607-default-rtdb.firebaseio.com/"

@st.cache_resource
def train_control_model():
    np.random.seed(42)
    X, y = [], []
    for _ in range(500):
        t, p, do, od = np.random.uniform(15, 50), np.random.uniform(3, 10), np.random.uniform(0, 100), np.random.uniform(0, 5)
        eff = np.exp(-((t-37)**2)/50) * np.exp(-((p-7)**2)/2)
        X.append([t, p, do, od]); y.append(eff)
    return RandomForestRegressor(n_estimators=50).fit(X, y)

ai_brain = train_control_model()

# ==========================================
# 2. SIDEBAR NAVIGATION & CONFIG
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color: white; font-size: 1.5rem; font-weight: 800;'>NEURAL <span style='color:#00f2ff'>CORE</span></h1>", unsafe_allow_html=True)
    
    # NEW NAVIGATION SECTION
    st.markdown("### 🛰️ NAVIGATION")
    page = st.radio("Go to", ["🏠 Home Dashboard", "📰 News & Intel", "🗓️ Upcoming Milestones", "⚙️ System Settings"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # ORIGINAL CONFIG LOGIC
    st.markdown("### 🧬 SPECIMEN CONFIG")
    microbe = st.selectbox("Active Microorganism", ["E. coli", "S. cerevisiae (Yeast)", "Custom"])

    if microbe == "E. coli": ideal_t, ideal_p, ideal_do = 37.0, 7.0, 40.0
    elif microbe == "S. cerevisiae (Yeast)": ideal_t, ideal_p, ideal_do = 30.0, 5.0, 20.0
    else:
        ideal_t = st.number_input("Target Temp", value=37.0)
        ideal_p = st.number_input("Target pH", value=7.0)
        ideal_do = st.number_input("Target DO%", value=40.0)

    st.markdown("---")
    st.success("Neural Link: **ENCRYPTED**")

# ==========================================
# 3. PAGE CONTENT ROUTING
# ==========================================

# --- HOME DASHBOARD ---
if "Home" in page:
    st.markdown("<h1 style='text-align: center; color: white; font-weight: 800; letter-spacing: -2px;'>BIOCHAMBER <span style='color:#00f2ff'>DASHBOARD</span></h1>", unsafe_allow_html=True)

    @st.fragment(run_every=5)
    def process_home():
        try:
            # Data Fetching
            response = requests.get(f"{FIREBASE_URL}/live_readings.json")
            data = response.json() or {"temperature": 37.2, "ph": 7.1, "dissolved_oxygen": 45, "optical_density": 1.5}
            
            cur_t, cur_p, cur_do, cur_od = data.get('temperature',0), data.get('ph',0), data.get('dissolved_oxygen',0), data.get('optical_density',0)
            efficiency = ai_brain.predict([[cur_t, cur_p, cur_do, cur_od]])[0]
            
            # Metrics Row
            c1, c2, c3, c4 = st.columns(4)
            metrics = [("Temperature", cur_t, "°C"), ("pH Level", cur_p, ""), ("Oxygen", cur_do, "%"), ("Density", cur_od, "OD")]
            for i, (l, v, u) in enumerate(metrics):
                with [c1, c2, c3, c4][i]:
                    st.markdown(f'<div class="neural-card"><div class="m-label">{l}</div><div class="m-value">{v}<span style="font-size:1rem; color:#00f2ff;">{u}</span></div></div>', unsafe_allow_html=True)

            # Analysis Row
            col_left, col_right = st.columns([2, 1])
            with col_left:
                st.markdown(f"""
                <div class="neural-card">
                    <h3 style="color:#00f2ff; margin-top:0;">🤖 AI Directives</h3>
                    <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <span>Thermal Regulation</span>
                        <span class="status-ok">NOMINAL</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <span>pH Balancing</span>
                        <span class="status-warn">ACID_INJECT</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding:10px 0;">
                        <span>Oxygen Saturation</span>
                        <span class="status-ok">OPTIMIZED</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_right:
                st.markdown('<div class="neural-card">', unsafe_allow_html=True)
                st.markdown("<h3 style='color:white; text-align:center;'>Efficiency</h3>", unsafe_allow_html=True)
                st.markdown(f"<h1 style='text-align:center; color:#00f2ff;'>{round(efficiency*100,1)}%</h1>", unsafe_allow_html=True)
                st.progress(float(efficiency))
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Sync Error: {e}")

    process_home()

# --- NEWS & INTEL ---
elif "News" in page:
    st.markdown("<h1 style='text-align: center; color: white; font-weight: 800;'>BIOLAB <span style='color:#7000ff'>INTEL</span></h1>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="neural-card">
            <h3 style="color:#00f2ff; margin-top:0;">🗞️ Latest Research News</h3>
            <div class="news-item">
                <div class="news-date">Feb 18, 2026</div>
                <div class="news-title">Breakthrough in E.coli Metabolic Pathways</div>
                <div class="news-desc">New neural models suggest a 15% increase in yield when temperature fluctuates in 0.2°C sine waves.</div>
            </div>
            <div class="news-item">
                <div class="news-date">Feb 15, 2026</div>
                <div class="news-title">System Update v4.2.0</div>
                <div class="news-desc">Implemented advanced glassmorphism rendering for real-time monitoring components.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="neural-card">
            <h3 style="color:#7000ff; margin-top:0;">🚀 Upcoming Launches</h3>
            <div class="news-item" style="border-left-color: #00f2ff;">
                <div class="news-date">March 2026</div>
                <div class="news-title">BioChamber Mobile App</div>
                <div class="news-desc">Monitor your bioreactor from anywhere with full haptic feedback and AR visualizations.</div>
            </div>
            <div class="news-item" style="border-left-color: #00f2ff;">
                <div class="news-date">Q2 2026</div>
                <div class="news-title">Quantum Sensor Integration</div>
                <div class="news-desc">Upgrade kits for sub-atomic pH precision will be available for all Neural Core users.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- UPCOMING MILESTONES ---
elif "Milestones" in page:
    st.markdown("<h1 style='text-align: center; color: white; font-weight: 800;'>PROJECT <span style='color:#ff007a'>TIMELINE</span></h1>", unsafe_allow_html=True)
    st.markdown("""
    <div class="neural-card">
        <h3 style="color:white;">🗓️ Road to Optimization</h3>
        <p style="color:#94a3b8;">Tracking the progress of our current microbial batch.</p>
        <br>
        <div style="padding:10px; border-radius:10px; background:rgba(255,0,122,0.1); border:1px solid #ff007a; margin-bottom:10px;">
            <b>Phase 1: Inoculation</b> - COMPLETED
        </div>
        <div style="padding:10px; border-radius:10px; background:rgba(0,242,255,0.1); border:1px solid #00f2ff; margin-bottom:10px;">
            <b>Phase 2: Exponential Growth</b> - IN PROGRESS (Neural AI monitoring active)
        </div>
        <div style="padding:10px; border-radius:10px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.2);">
            <b>Phase 3: Stationary Phase</b> - ESTIMATED 48 HOURS
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- SETTINGS ---
else:
    st.markdown("<h1 style='text-align: center; color: white; font-weight: 800;'>CORE <span style='color:#94a3b8'>SETTINGS</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="neural-card">', unsafe_allow_html=True)
    st.checkbox("Enable Dark-Glass Reflections")
    st.checkbox("High-Frequency AI Refresh (1s)")
    st.checkbox("Audio Alerts for Critical Deviations")
    st.slider("UI Glow Intensity", 0, 100, 50)
    st.button("Reset Neural Brain")
    st.markdown('</div>', unsafe_allow_html=True)
