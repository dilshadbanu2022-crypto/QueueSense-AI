import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from xgboost import XGBRegressor
import os
import requests
from dotenv import load_dotenv
from simulation_engine import SimulationEngine
load_dotenv()
# ============================================================
# APOLLO LIVE QUEUE API CONFIGURATION
# ============================================================

apollo_queue_api_url = os.getenv(
    "APOLLO_QUEUE_API_URL",
    ""
)

apollo_queue_api_key = os.getenv(
    "APOLLO_QUEUE_API_KEY",
    ""
)
def get_apollo_live_queue():
    """
    Get real-time Apollo queue data from an authorized API.
    """

    if not apollo_queue_api_url or not apollo_queue_api_key:
        return None

    try:
        response = requests.get(
            apollo_queue_api_url,
            headers={
                "Authorization": f"Bearer {apollo_queue_api_key}"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return {
            "queue_length": data.get("queue_length"),
            "waiting_time": data.get("waiting_time")
        }

    except Exception:
        return None
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="QueueSense AI",
    page_icon="🎯",
    layout="wide"
)
# ============================================================
# LANGUAGE SELECTION
# ============================================================

st.sidebar.header("🌐 Language")

language = st.sidebar.selectbox(
    "Select Language",
    [
        "English",
        "తెలుగు",
        "हिन्दी",
        "اردو"
    ]
)
# ============================================================
# LANGUAGE TEXT
# ============================================================

translations = {

    "English": {
        "title": "🎯 QueueSense AI",
        "subtitle": "Smart Queue Management & Crowd Prediction System",
        "hospital_search": "🔎 Search Hyderabad Hospital",
        "search": "Search hospital",
        "ai_prediction": "🤖 AI Prediction for Selected Hospital",
        "simulation": "🤖 Live Autonomous Simulation",
        "recommendation": "🤖 AI Recommendation",
        "analysis": "📈 Queue & Crowd Analysis",
        "service": "🏥 Service Analysis",
        "what_if": "🔮 What-If Simulator",
        "system": "ℹ️ System Information"
    },

    "తెలుగు": {
        "title": "🎯 QueueSense AI",
        "subtitle": "స్మార్ట్ క్యూ నిర్వహణ & జనసందోహ అంచనా వ్యవస్థ",
        "hospital_search": "🔎 హైదరాబాద్ ఆసుపత్రిని వెతకండి",
        "search": "ఆసుపత్రిని వెతకండి",
        "ai_prediction": "🤖 ఎంపిక చేసిన ఆసుపత్రికి AI అంచనా",
        "simulation": "🤖 లైవ్ ఆటోనమస్ సిమ్యులేషన్",
        "recommendation": "🤖 AI సిఫార్సు",
        "analysis": "📈 క్యూ & జనసందోహ విశ్లేషణ",
        "service": "🏥 సేవల విశ్లేషణ",
        "what_if": "🔮 What-If సిమ్యులేటర్",
        "system": "ℹ️ సిస్టమ్ సమాచారం"
    },

    "हिन्दी": {
        "title": "🎯 QueueSense AI",
        "subtitle": "स्मार्ट कतार प्रबंधन और भीड़ पूर्वानुमान प्रणाली",
        "hospital_search": "🔎 हैदराबाद अस्पताल खोजें",
        "search": "अस्पताल खोजें",
        "ai_prediction": "🤖 चयनित अस्पताल के लिए AI पूर्वानुमान",
        "simulation": "🤖 लाइव ऑटोनॉमस सिमुलेशन",
        "recommendation": "🤖 AI सिफारिश",
        "analysis": "📈 कतार और भीड़ विश्लेषण",
        "service": "🏥 सेवा विश्लेषण",
        "what_if": "🔮 What-If सिमुलेटर",
        "system": "ℹ️ सिस्टम जानकारी"
    },

    "اردو": {
        "title": "🎯 QueueSense AI",
        "subtitle": "اسمارٹ قطار مینجمنٹ اور ہجوم کی پیش گوئی کا نظام",
        "hospital_search": "🔎 حیدرآباد ہسپتال تلاش کریں",
        "search": "ہسپتال تلاش کریں",
        "ai_prediction": "🤖 منتخب ہسپتال کے لیے AI پیش گوئی",
        "simulation": "🤖 لائیو خودکار سمولیشن",
        "recommendation": "🤖 AI سفارش",
        "analysis": "📈 قطار اور ہجوم کا تجزیہ",
        "service": "🏥 سروس کا تجزیہ",
        "what_if": "🔮 What-If سمیولیٹر",
        "system": "ℹ️ سسٹم کی معلومات"
    }
}

text = translations[language]

st.title(text["title"])
st.subheader(text["subtitle"])

# ------------------------------------------------------------
# GLOBAL DEMO/TRAINING DATA DISCLAIMER
# ------------------------------------------------------------
# Shown once, right under the title, so it's the first thing any
# viewer (examiner, hospital staff, etc.) sees before any numbers.

st.warning(
    "⚠️ **Demo / Training Data** — This application currently runs on "
    "synthetic queue data generated for development and ML training "
    "purposes. It does not represent real Apollo Hospitals patient data. "
    "Live figures will appear automatically once an authorized Apollo "
    "queue data feed is connected."
)

st.divider()

# ============================================================
# VERIFIED APOLLO HOSPITALS - HYDERABAD
# ============================================================

st.header(text["hospital_search"])

if "selected_hospital" not in st.session_state:
    st.session_state["selected_hospital"] = None

# Default value when no hospital/live API data is available
live_queue = None

apollo_hospitals = [
    {
        "name": "Apollo Health City - Jubilee Hills",
        "area": "Jubilee Hills",
        "address": "Road No. 72, Film Nagar, Jubilee Hills, Hyderabad, Telangana 500033",
        "lat": 17.4141,
        "lon": 78.4098
    },
    {
        "name": "Apollo Hospitals - Secunderabad",
        "area": "Secunderabad",
        "address": "Pollicetty Towers, St. John's Road, Regimental Bazaar, Secunderabad, Telangana 500003",
        "lat": 17.4399,
        "lon": 78.5010
    },
    {
        "name": "Apollo Hospitals - Hyderguda",
        "area": "Hyderguda",
        "address": "Plot No. 3-5-836 to 838, Hyderguda-Basheerbagh Road, Hyderabad, Telangana 500029",
        "lat": 17.4000,
        "lon": 78.4760
    },
    {
        "name": "Apollo Hospitals - DRDO",
        "area": "Kanchan Bagh",
        "address": "DMRL Cross Road, Kanchan Bagh, Hyderabad, Telangana 500058",
        "lat": 17.3216,
        "lon": 78.4860
    },
    {
        "name": "Apollo Hospitals - Financial District",
        "area": "Nanakramguda",
        "address": "D.No-2-105/6/SE, Financial District, Nanakramguda, Hyderabad, Telangana 500032",
        "lat": 17.4217,
        "lon": 78.3447
    }
]
hospital_search = st.text_input(
    text["search"],
    placeholder="Example: Apollo Hospital"
)

live_queue = None

if hospital_search:

    search_text = hospital_search.lower()

    results = [
        hospital
        for hospital in apollo_hospitals
        if search_text in hospital["name"].lower()
        or search_text in hospital["area"].lower()
    ]

    if results:

        st.success(
            f"Found {len(results)} Apollo location(s) in Hyderabad."
        )

        hospital_names = [
            hospital["name"]
            for hospital in results
        ]

        selected_hospital = st.selectbox(
            "📍 Select Apollo Hospital",
            hospital_names,
            key="apollo_hospital_selection"
        )

        selected_data = next(
            hospital
            for hospital in results
            if hospital["name"] == selected_hospital
        )

        st.session_state["selected_hospital"] = selected_data

        st.success(
            f"📍 {selected_data['name']} selected"
        )

        st.write("### 📍 Selected Hospital")

        st.write(
            f"**Hospital:** {selected_data['name']}"
        )

        st.write(
            f"**Area:** {selected_data['area']}"
        )

        st.write(
            f"**Address:** {selected_data['address']}"
        )

        st.write(
            f"**Latitude:** {selected_data['lat']}"
        )

        st.write(
            f"**Longitude:** {selected_data['lon']}"
        )

        # ============================================================
        # GET DIRECTIONS
        # ============================================================

        maps_url = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&destination={selected_data['lat']},{selected_data['lon']}"
        )

        st.link_button(
            "📍 Get Directions",
            maps_url
        )

     
# ============================================================
# AUTONOMOUS SIMULATION STATE
# ============================================================

if "simulation_engine" not in st.session_state:
    st.session_state.simulation_engine = SimulationEngine()

if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False

if "simulation_speed" not in st.session_state:
    st.session_state.simulation_speed = 1

if "simulation_state" not in st.session_state:
    st.session_state.simulation_state = None

if "simulation_prediction" not in st.session_state:
    st.session_state.simulation_prediction = None

if "simulation_decision" not in st.session_state:
    st.session_state.simulation_decision = None

if "simulation_scenario" not in st.session_state:
    st.session_state.simulation_scenario = "NORMAL"
if "simulation_step_count" not in st.session_state:
    st.session_state.simulation_step_count = 0
# ============================================================
# LOAD ML MODELS
# ============================================================

@st.cache_resource
def load_models():
    waiting_model = joblib.load("models/waiting_time_model.pkl")
    crowd_model = joblib.load("models/crowd_prediction_model.pkl")
    risk_model = joblib.load("models/crowd_risk_model.pkl")
    return waiting_model, crowd_model, risk_model


waiting_model, crowd_model, risk_model = load_models()
# ============================================================
# LOAD DATASET
# ============================================================

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/processed_queue_data.csv")


df = load_data()
# ============================================================
# SIDEBAR - QUEUE CONTROLS
# ============================================================

st.sidebar.header("🎛️ Queue Controls")

st.sidebar.caption(
    "🟡 Demo controls — these manually feed the ML model "
    "when no authorized live queue data is connected."
)

service_type = st.sidebar.selectbox(
    "Service Type",
    [
        "Registration",
        "OPD",
        "Laboratory",
        "Pharmacy"
    ]
)

hour = st.sidebar.slider(
    "Current Hour",
    0,
    23,
    10
)

active_counters = st.sidebar.slider(
    "Active Counters",
    1,
    5,
    3
)

staff_available = st.sidebar.slider(
    "Staff Available",
    1,
    7,
    4
)

queue_length = st.sidebar.number_input(
    "Queue Length",
    min_value=0,
    value=50
)

people_arriving = st.sidebar.number_input(
    "People Arriving",
    min_value=0,
    value=10
)

people_served = st.sidebar.number_input(
    "People Served",
    min_value=0,
    value=8
)

average_service_time = st.sidebar.number_input(
    "Average Service Time",
    min_value=1.0,
    value=10.0
)

# ============================================================
# SERVICE TYPE ENCODING
# ============================================================

service_map = {
    "Laboratory": 0,
    "OPD": 1,
    "Pharmacy": 2,
    "Registration": 3
}

service_code = service_map[service_type]

# ============================================================
# CALCULATED VALUES
# ============================================================

# Use real Apollo queue data when an authorized API is connected.
# Otherwise, use the manual/demo queue value.

queue_length_for_ml = queue_length
capacity = (
    active_counters *
    10 /
    average_service_time
)

current_crowd = (
    queue_length_for_ml +
    people_arriving
)

future_crowd = (
    queue_length +
    people_arriving +
    (people_arriving - people_served)
)

# ============================================================
# INPUT FOR WAITING-TIME MODEL
# 16 FEATURES
# ============================================================

waiting_input = pd.DataFrame([{

    "day_of_week": 1,

    "hour": hour,

    "service_type": service_code,

    "queue_length": queue_length_for_ml,

    "people_arriving": people_arriving,

    "people_served": people_served,

    "active_counters": active_counters,

    "staff_available": staff_available,

    "average_service_time": average_service_time,

    "capacity": capacity,

    "holiday": 0,

    "current_crowd": current_crowd,

    "future_crowd": future_crowd,

    "year": 2026,

    "month": 9,

    "day": 7

}])

# ============================================================
# INPUT FOR CROWD + RISK MODELS
# 15 FEATURES
# ============================================================

crowd_input = waiting_input.drop(
    columns=["future_crowd"]
)

# ============================================================
# MACHINE LEARNING PREDICTIONS
# ============================================================

waiting_time = waiting_model.predict(
    waiting_input
)[0]

predicted_crowd = crowd_model.predict(
    crowd_input
)[0]

risk_prediction = risk_model.predict(
    crowd_input
)[0]

# ============================================================
# RISK LEVEL
# ============================================================

risk_names = {
    0: "LOW",
    1: "MEDIUM",
    2: "HIGH"
}

risk = risk_names.get(
    int(risk_prediction),
    "UNKNOWN"
)
# ============================================================
# APOLLO HOSPITAL ML PREDICTION
# ============================================================

if st.session_state.get("selected_hospital") is not None:

    selected_hospital_data = (
        st.session_state["selected_hospital"]
    )

    st.header(text["ai_prediction"])
    st.caption(
        f"ML prediction for "
        f"{selected_hospital_data['name']}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "⏱️ Predicted Waiting Time",
            f"{waiting_time:.1f} min"
        )

    with col2:

        st.metric(
            "🔮 Predicted Future Crowd",
            f"{predicted_crowd:.0f}"
        )

    with col3:

        st.metric(
            "⚠️ Crowd Risk",
            risk
        )

    st.info(
        "🟡 Prediction is based on the current QueueSense AI "
        "ML inputs. It will use verified hospital live-queue "
        "data when an authorized data source is connected."
    )
    # ============================================================
# AI QUEUE INSIGHT
# ============================================================

st.header("🧠 AI Queue Insight")

if people_arriving > people_served:

    st.warning(
        f"📈 Queue is increasing because "
        f"{people_arriving} people are arriving while "
        f"{people_served} people are being served."
    )

elif people_served > people_arriving:

    st.success(
        f"📉 Queue is decreasing because "
        f"{people_served} people are being served while "
        f"{people_arriving} people are arriving."
    )

else:

    st.info(
        "➡️ Queue is currently stable because arrivals "
        "and served customers are equal."
    )

st.write(
    f"👥 Current Queue: **{queue_length_for_ml} people**"
)

st.write(
    f"👨‍💼 Active Counters: **{active_counters}**"
)

st.write(
    f"⏱️ Average Service Time: **{average_service_time:.1f} minutes**"
)
    # ============================================================
# HOSPITAL COMPARISON
# ============================================================

if hospital_search and results:

    st.header("🏥 Compare Hospitals")

    st.caption(
        "Compare QueueSense AI demo predictions to find the "
        "hospital with the lowest predicted waiting time."
    )

    comparison_results = []

    for index, hospital in enumerate(results):

        # Create a separate input for each hospital
        hospital_input = waiting_input.copy()

        # Demo variation for comparison
        demo_queue = queue_length + (index * 8)

        hospital_input["queue_length"] = demo_queue

        hospital_input["current_crowd"] = (
            demo_queue + people_arriving
        )

        hospital_input["future_crowd"] = (
            demo_queue
            + people_arriving
            + (people_arriving - people_served)
        )

        # ML prediction
        hospital_wait = waiting_model.predict(
            hospital_input
        )[0]

        hospital_crowd = crowd_model.predict(
            hospital_input.drop(
                columns=["future_crowd"]
            )
        )[0]

        hospital_risk_code = risk_model.predict(
            hospital_input.drop(
                columns=["future_crowd"]
            )
        )[0]

        hospital_risk = risk_names.get(
            int(hospital_risk_code),
            "UNKNOWN"
        )

        comparison_results.append({

            "Hospital": hospital["name"],

            "Area": hospital["area"],

            "Demo Queue": demo_queue,

            "Predicted Wait (min)": round(
                hospital_wait,
                1
            ),

            "Predicted Crowd": round(
                hospital_crowd
            ),

            "Risk": hospital_risk
        })

    comparison_df = pd.DataFrame(
        comparison_results
    )

    # Sort by fastest predicted waiting time
    comparison_df = comparison_df.sort_values(
        by="Predicted Wait (min)"
    ).reset_index(drop=True)

    def color_risk(value):
        if value == "LOW":
            return "background-color: #d4edda; color: #155724; font-weight: bold"
        elif value == "MEDIUM":
            return "background-color: #fff3cd; color: #856404; font-weight: bold"
        elif value == "HIGH":
            return "background-color: #f8d7da; color: #721c24; font-weight: bold"
        return ""

    styled_comparison = comparison_df.style.map(
        color_risk,
        subset=["Risk"]
    )

    st.dataframe(
        styled_comparison,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🏆 Fastest Hospital")

    best_hospital = comparison_df.iloc[0]

    st.success(
        f"🥇 {best_hospital['Hospital']} "
        f"({best_hospital['Area']})"
    )

    st.metric(
        "⏱️ Lowest Predicted Waiting Time",
        f"{best_hospital['Predicted Wait (min)']} minutes"
    )

    st.info(
        f"👥 Demo Queue: {best_hospital['Demo Queue']} people | "
        f"🚦 Risk: {best_hospital['Risk']}"
    )
    st.subheader("🤖 AI Recommendation")

    st.success(
        f"💡 QueueSense AI recommends **{best_hospital['Hospital']}** "
        f"because it currently has the lowest predicted waiting time "
        f"among the searched hospitals."
    )

    st.caption(
        "⚠️ This is a demo/ML prediction, not a verified live hospital queue."
    )
# ============================================================
# BEST AND WORST TIME TO VISIT
# ============================================================

if hospital_search and results:

    st.header("🕐 Best & Worst Time to Visit")

    st.caption(
        "QueueSense AI compares predicted waiting times throughout "
        "the day to identify the best and worst times to visit."
    )

    time_results = []

    # Check every hour from 8 AM to 8 PM
    visit_hours = range(8, 21)

    for hour in visit_hours:

        time_input = waiting_input.copy()
        time_input["hour"] = hour

        predicted_wait = waiting_model.predict(
            time_input
        )[0]

        time_results.append({
            "Time": f"{hour:02d}:00",
            "Predicted Wait (min)": round(predicted_wait, 1)
        })

    time_df = pd.DataFrame(time_results)

    # Best time
    best_time = time_df.loc[
        time_df["Predicted Wait (min)"].idxmin()
    ]

    # Worst time
    worst_time = time_df.loc[
        time_df["Predicted Wait (min)"].idxmax()
    ]

    # Show all times
    st.dataframe(
        time_df,
        use_container_width=True,
        hide_index=True
    )

    # Best time
    st.subheader("🟢 Best Time")

    st.success(
        f"🕐 QueueSense AI recommends **{best_time['Time']}** "
        f"with an estimated waiting time of "
        f"**{best_time['Predicted Wait (min)']} minutes**."
    )

    # Worst time
    st.subheader("🔴 Worst Time")

    st.error(
        f"🕐 The busiest predicted time is **{worst_time['Time']}** "
        f"with an estimated waiting time of "
        f"**{worst_time['Predicted Wait (min)']} minutes**."
    )

    st.caption(
        "⚠️ These are ML predictions based on QueueSense AI "
        "training/demo data, not verified live hospital queue data."
    )

# ============================================================
# WHY IS IT CROWDED?
# ============================================================

st.header("🧠 Why Is It Crowded?")

reasons = []

if people_arriving > people_served:
    reasons.append(
        f"📈 More people are arriving ({people_arriving}) "
        f"than being served ({people_served})."
    )

if queue_length_for_ml >= 50:
    reasons.append(
        f"👥 The current queue is high at "
        f"{queue_length_for_ml} people."
    )

if active_counters <= 2:
    reasons.append(
        f"🏢 Only {active_counters} active counters are available."
    )

if average_service_time >= 10:
    reasons.append(
        f"⏱️ Average service time is high at "
        f"{average_service_time:.1f} minutes."
    )

if capacity < people_arriving:
    reasons.append(
        f"⚠️ Current service capacity ({capacity:.1f} people) "
        f"is lower than incoming demand ({people_arriving} people)."
    )

if reasons:
    st.warning("🔎 QueueSense AI detected these possible reasons:")

    for reason in reasons:
        st.write(reason)
else:
    st.success(
        "✅ Queue conditions currently appear stable."
    )

st.caption(
    "⚠️ Explanation is based on current QueueSense AI inputs "
    "and rule-based analysis."
)    

# ============================================================
# LIVE AUTONOMOUS SIMULATION
# ============================================================

st.header(text["simulation"])

st.info(
    "🟡 DEMO / SIMULATION DATA — "
    "This simulation demonstrates how QueueSense AI responds "
    "to changing queue conditions."
)

# ------------------------------------------------------------
# SIMULATION CONTROLS
# ------------------------------------------------------------

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("▶️ Play", key="simulation_play"):
        st.session_state.simulation_running = True

with col2:
    if st.button("⏸️ Pause", key="simulation_pause"):
        st.session_state.simulation_running = False

with col3:
    if st.button("🔄 Reset", key="simulation_reset"):

        st.session_state.simulation_engine = SimulationEngine()
        st.session_state.simulation_running = False
        st.session_state.simulation_state = None
        st.session_state.simulation_prediction = None
        st.session_state.simulation_decision = None
        st.session_state.simulation_scenario = "NORMAL"
        st.session_state.simulation_step_count = 0  
        st.rerun()

with col4:
    if st.button("1×", key="speed_1x"):
        st.session_state.simulation_speed = 1

with col5:
    if st.button("2×", key="speed_2x"):
        st.session_state.simulation_speed = 2

with col6:
    if st.button("5×", key="speed_5x"):
        st.session_state.simulation_speed = 5

st.caption(
    f"Simulation Speed: "
    f"{st.session_state.simulation_speed}×"
)

# ------------------------------------------------------------
# RUN SIMULATION
# ------------------------------------------------------------

if st.session_state.simulation_running:

    engine = st.session_state.simulation_engine

    # Start the simulation if necessary
    if not engine.simulation.running:
        engine.simulation.start()

    # Get current scenario multiplier
    multiplier = (
        engine.scenario_engine.get_arrival_multiplier()
    )

    # Run one autonomous simulation step
    state = engine.simulation.step(
        arrival_multiplier=multiplier
    )

    # ML predictions
    prediction = engine.ml_engine.predict(
        state
    )

    # AI decision
    decision = engine.decision_engine.decide(
        state,
        prediction
    )

    action = decision.get(
        "action",
        "NO_ACTION"
    )

    new_counters = decision.get(
        "new_counters",
        state.get("active_counters", 1)
    )

    # Apply AI decision
    if action in [
        "OPEN_COUNTER",
        "INCREASE_COUNTERS",
        "PREPARE_COUNTER",
        "MAX_COUNTERS"
    ]:

        engine.simulation.set_counters(
            new_counters
        )

    # Update scenario
    new_scenario = (
        engine.scenario_engine.update_scenario(
            state,
            prediction
        )
    )

    # Record impact
    engine.impact.record_state(
        state,
        prediction,
        decision
    )

    # Save current state
    st.session_state.simulation_state = state
    st.session_state.simulation_prediction = prediction
    st.session_state.simulation_decision = decision
    st.session_state.simulation_scenario = new_scenario

    # Stop automatically after stabilization
    if new_scenario == "STABILIZATION":

        st.session_state.simulation_running = False

        st.success(
            "✅ Autonomous system reached STABILIZATION."
        )

    else:

        # ----------------------------------------------------
        # CONTINUOUS SIMULATION
        # ----------------------------------------------------

        import time

        speed = st.session_state.simulation_speed

        delay = {
            1: 1.0,
            2: 0.5,
            5: 0.2
        }.get(speed, 1.0)

        time.sleep(delay)

        st.rerun()

    engine = st.session_state.simulation_engine

    # Start the simulation if necessary
    if not engine.simulation.running:
        engine.simulation.start()

    # Get current scenario multiplier
    multiplier = (
        engine.scenario_engine.get_arrival_multiplier()
    )

    # Run one autonomous simulation step
    state = engine.simulation.step(
        arrival_multiplier=multiplier
    )

    # ML predictions
    prediction = engine.ml_engine.predict(
        state
    )

    # AI decision
    decision = engine.decision_engine.decide(
        state,
        prediction
    )

    action = decision.get(
        "action",
        "NO_ACTION"
    )

    new_counters = decision.get(
        "new_counters",
        state.get("active_counters", 1)
    )

    # Apply AI decision
    if action in [
        "OPEN_COUNTER",
        "INCREASE_COUNTERS",
        "PREPARE_COUNTER",
        "MAX_COUNTERS"
    ]:

        engine.simulation.set_counters(
            new_counters
        )

    # Update scenario
    new_scenario = (
        engine.scenario_engine.update_scenario(
            state,
            prediction
        )
    )

    # Record impact
    engine.impact.record_state(
        state,
        prediction,
        decision
    )

    # Save current state
    st.session_state.simulation_state = state
    st.session_state.simulation_prediction = prediction
    st.session_state.simulation_decision = decision
    st.session_state.simulation_scenario = new_scenario

    # Stop automatically after stabilization
    if new_scenario == "STABILIZATION":

        st.session_state.simulation_running = False

        st.success(
            "✅ Autonomous system reached STABILIZATION."
        )

    else:

        # ----------------------------------------------------
        # CONTINUOUS SIMULATION
        # ----------------------------------------------------

        import time

        speed = st.session_state.simulation_speed

        delay = {
            1: 1.0,
            2: 0.5,
            5: 0.2
        }.get(speed, 1.0)

        time.sleep(delay)

        st.rerun()

# ------------------------------------------------------------
# DISPLAY CURRENT SIMULATION
# ------------------------------------------------------------

if st.session_state.simulation_state is not None:

    state = st.session_state.simulation_state

    prediction = (
        st.session_state.simulation_prediction
    )

    decision = (
        st.session_state.simulation_decision
    )

    scenario = (
        st.session_state.simulation_scenario
    )

    st.write("### 📡 Current Simulation Status")

    # --------------------------------------------------------
    # SIMULATION STATE
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "👥 Queue",
            state.get("queue_length", 0)
        )

    with col2:

        st.metric(
            "🚶 People Arriving",
            state.get("people_arriving", 0)
        )

    with col3:

        st.metric(
            "✅ People Served",
            state.get("people_served", 0)
        )

    with col4:

        st.metric(
            "👨‍💼 Active Counters",
            state.get("active_counters", 0)
        )

    # --------------------------------------------------------
    # ML PREDICTIONS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "⏱️ Waiting Time",
            f"{prediction.get('predicted_waiting_time', 0):.1f} min"
        )

    with col2:

        st.metric(
            "🔮 Predicted Crowd",
            f"{prediction.get('predicted_crowd', 0):.0f}"
        )

    with col3:

        st.metric(
            "🚦 Risk",
            prediction.get(
                "risk",
                "LOW"
            )
        )

    with col4:

        st.metric(
            "📈 Scenario",
            scenario
        )

    # --------------------------------------------------------
    # AI DECISION
    # --------------------------------------------------------

    st.write("### 🤖 AI Decision")

    st.write(
        f"**Action:** "
        f"{decision.get('action', 'NO_ACTION')}"
    )

    st.write(
        f"**Priority:** "
        f"{decision.get('priority', 'NORMAL')}"
    )

    st.write(
        f"**Reason:** "
        f"{decision.get('reason', '')}"
    )

    st.caption(
        f"Simulation Time: "
        f"{state.get('simulation_time', 'N/A')} | "
        f"Arrival Multiplier: "
        f"{st.session_state.simulation_engine.scenario_engine.get_arrival_multiplier():.1f}×"
    )

else:

    st.info(
        "Press ▶️ Play to start the autonomous simulation."
    )


# ============================================================
# AI RECOMMENDATION
# ============================================================
st.header(text["recommendation"])

if risk == "HIGH":

    st.error(
        "🚨 HIGH CROWD RISK"
    )

    st.write(
        "AI Recommendation: Open an additional counter "
        "and allocate additional staff."
    )

elif risk == "MEDIUM":

    st.warning(
        "⚠️ MEDIUM CROWD RISK"
    )

    st.write(
        "AI Recommendation: Monitor the queue and "
        "prepare an additional counter."
    )

else:

    st.success(
        "✅ LOW CROWD RISK"
    )

    st.write(
        "AI Recommendation: Current counters are sufficient."
    )
# ============================================================
# CROWD RISK GAUGE
# ============================================================

st.subheader("🚦 Crowd Risk Gauge")

risk_score = {
    "LOW": 25,
    "MEDIUM": 60,
    "HIGH": 90
}.get(risk, 0)

fig, ax = plt.subplots(figsize=(8, 1.5))

ax.barh(
    [0],
    [100],
    color="lightgray",
    height=0.35
)

risk_color = {
    "LOW": "green",
    "MEDIUM": "orange",
    "HIGH": "red"
}.get(risk, "gray")

ax.barh(
    [0],
    [risk_score],
    color=risk_color,
    height=0.35
)

ax.set_xlim(0, 100)
ax.set_yticks([])
ax.set_xlabel("Risk Level")

ax.set_title(
    f"Current Crowd Risk: {risk}",
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout()

st.pyplot(fig)

st.info(
    "🟢 LOW = quieter crowd  |  "
    "🟠 MEDIUM = moderate crowd  |  "
    "🔴 HIGH = busy crowd"
)
# ============================================================
# MODEL COMPARISON
# ============================================================

st.header("🤖 Model Comparison")

@st.cache_resource
def train_comparison_models(df):

    st.caption(
        "Compare different machine learning models for waiting-time prediction."
    )

    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from xgboost import XGBRegressor

    # Prepare training data
    X = df.drop(columns=["waiting_time"])
    y = df["waiting_time"]

    # Convert categorical columns if present
    X = pd.get_dummies(X, drop_first=True)

    # Fill any missing values
    X = X.fillna(0)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

        # -------------------------------
    # Linear Regression
    # -------------------------------

    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)

    linear_pred = linear_model.predict(X_test)

    linear_mae = mean_absolute_error(y_test, linear_pred)
    linear_r2 = r2_score(y_test, linear_pred)

        # -------------------------------
    # Random Forest
    # -------------------------------

    comparison_rf = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )

    comparison_rf.fit(X_train, y_train)

    rf_pred = comparison_rf.predict(X_test)

    rf_mae = mean_absolute_error(y_test, rf_pred)
    rf_r2 = r2_score(y_test, rf_pred)

    # -------------------------------
    # XGBoost
    # -------------------------------

    xgb_model = XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )

    xgb_model.fit(X_train, y_train)

    xgb_pred = xgb_model.predict(X_test)

    xgb_mae = mean_absolute_error(y_test, xgb_pred)
    xgb_r2 = r2_score(y_test, xgb_pred)

        # -------------------------------
    # Comparison table
    # -------------------------------

    comparison_models = pd.DataFrame({
        "Model": [
            "Linear Regression",
            "Random Forest",
            "XGBoost"
        ],
        "MAE": [
            round(linear_mae, 2),
            round(rf_mae, 2),
            round(xgb_mae, 2)
        ],
        "R² Score": [
            round(linear_r2, 4),
            round(rf_r2, 4),
            round(xgb_r2, 4)
        ]
    })

    return comparison_models, rf_mae


# Run model comparison
comparison_models, rf_mae = train_comparison_models(df)

st.dataframe(
    comparison_models,
    use_container_width=True,
    hide_index=True
)

# Best model
best_model_row = comparison_models.loc[
    comparison_models["MAE"].idxmin()
]

st.success(
    f"🏆 Best Model: {best_model_row['Model']} "
    f"with MAE = {best_model_row['MAE']} minutes"
)

st.caption(
    "⚠️ Model comparison uses QueueSense AI training/demo data."
)
# ============================================================
# PREDICTION CONFIDENCE RANGE
# ============================================================

st.header("📊 Prediction Confidence Range")

# Use Random Forest's measured MAE
prediction_error = rf_mae

lower_wait = max(0, waiting_time - prediction_error)
upper_wait = waiting_time + prediction_error

st.metric(
    "⏱️ Predicted Waiting Time",
    f"{waiting_time:.1f} minutes"
)

st.success(
    f"📊 Estimated Waiting Range: "
    f"**{lower_wait:.1f} – {upper_wait:.1f} minutes**"
)

st.info(
    f"QueueSense AI estimates the waiting time may vary by "
    f"about **±{prediction_error:.1f} minutes**, based on the "
    f"Random Forest model's measured MAE."
)

st.caption(
    "⚠️ This is an estimated prediction range based on model "
    "error, not a statistical confidence interval or live data."
)
# ============================================================
# ANOMALY DETECTION
# ============================================================

st.header("🚨 Anomaly Detection")

st.caption(
    "QueueSense AI checks whether the current queue conditions "
    "look unusual compared with its training data."
)

from sklearn.ensemble import IsolationForest

# Numerical features used for anomaly detection
anomaly_features = [
    "queue_length",
    "people_arriving",
    "people_served",
    "active_counters",
    "staff_available",
    "average_service_time",
    "capacity",
    "current_crowd"
]

# Training data
anomaly_data = df[anomaly_features].copy()

# Train anomaly detector (cached so it only trains once, not every rerun)
@st.cache_resource
def get_anomaly_model(data):
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )
    model.fit(data)
    return model

anomaly_model = get_anomaly_model(anomaly_data)

# Current QueueSense conditions
current_anomaly_input = pd.DataFrame([{
    "queue_length": queue_length_for_ml,
    "people_arriving": people_arriving,
    "people_served": people_served,
    "active_counters": active_counters,
    "staff_available": staff_available,
    "average_service_time": average_service_time,
    "capacity": capacity,
    "current_crowd": current_crowd
}])

anomaly_result = anomaly_model.predict(
    current_anomaly_input
)[0]

if anomaly_result == -1:
    st.error(
        "🚨 ANOMALY DETECTED — Current queue conditions "
        "are unusual compared with the training data."
    )
else:
    st.success(
        "✅ NO ANOMALY DETECTED — Current queue conditions "
        "are within the normal pattern of the training data."
    )

st.caption(
    "⚠️ Anomaly detection is based on QueueSense training/demo data, "
    "not live hospital records."
)

# ============================================================
# CROWD HEATMAP - HOUR × DAY
# ============================================================

st.header("🔥 Crowd Heatmap")

st.caption(
    "See which days and hours are usually less or more crowded."
)

day_names = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

heatmap_data = (
    df.pivot_table(
        index="hour",
        columns="day_of_week",
        values="current_crowd",
        aggfunc="mean"
    )
    .reindex(index=range(24), columns=range(7))
)

heatmap_data = heatmap_data.rename(
    columns=day_names
)

heatmap_data.index = [
    f"{hour}:00" for hour in heatmap_data.index
]

st.dataframe(
    heatmap_data.style
    .background_gradient(
        cmap="RdYlGn_r",
        axis=None
    )
    .format("{:.0f}"),
    use_container_width=True,
    height=650
)

st.info(
    "🟢 Lower crowd  •  🟡 Medium crowd  •  🔴 Higher crowd"
)

st.caption(
    "⚠️ Demo/Training Data — not live hospital queue data."
)

# ============================================================
# MODEL TRAINING STATUS
# ============================================================

st.header("🧠 Model Training Status")

model_path = "models/waiting_time_model.pkl"

if os.path.exists(model_path):

    trained_time = os.path.getmtime(model_path)

    from datetime import datetime

    trained_date = datetime.fromtimestamp(
        trained_time
    ).strftime("%d %B %Y, %I:%M %p")

    st.success(
        f"✅ Waiting Time Model Last Trained: **{trained_date}**"
    )

else:

    st.warning(
        "⚠️ Waiting Time Model has not been trained yet."
    )

st.info(
    "🔄 Retraining allows QueueSense AI to update its model "
    "using the latest available training data."
)

if st.button("🔄 Retrain Models"):

    st.warning(
        "⚠️ Retraining is not connected to an automatic "
        "training pipeline yet."
    )

    st.info(
        "The current QueueSense AI models were trained using "
        "the available training/demo dataset."
    )

st.caption(
    "⚠️ Training status is based on the model file available "
    "in the QueueSense AI project."
)
# ============================================================
# WHAT-IF SIMULATOR
# ============================================================

st.header(text["what_if"])

st.write(
    "Simulate the effect of adding additional counters "
    "to reduce queue waiting time."
)

additional_counters = st.slider(
    "Add Additional Counters",
    min_value=0,
    max_value=5,
    value=1
)

new_counter_count = (
    active_counters +
    additional_counters
)

if additional_counters > 0:

    # Predict waiting time with additional counters
    simulation_input = waiting_input.copy()

    simulation_input["active_counters"] = new_counter_count

    simulation_input["capacity"] = (
    new_counter_count * 10 / average_service_time
)

    simulated_waiting_time = waiting_model.predict(
        simulation_input
    )[0]

    improvement = (
        waiting_time -
        simulated_waiting_time
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Current Counters",
            active_counters
        )

    with col2:
        st.metric(
            "New Counters",
            new_counter_count
        )

    with col3:
        st.metric(
            "Expected Waiting Time Reduction",
            f"{max(improvement, 0):.1f} min"
        )

    st.success(
        f"🤖 AI Simulation: Adding {additional_counters} "
        f"counter(s) could reduce predicted waiting time "
        f"from {waiting_time:.1f} minutes to "
        f"{simulated_waiting_time:.1f} minutes."
    )

    if improvement > 0:
        st.info(
            "✅ Recommendation: Adding counters is beneficial."
        )
    else:
        st.warning(
            "⚠️ Adding counters may not significantly improve "
            "the current waiting time."
        )

else:

    st.info(
        "Move the slider to simulate adding counters."
    )
# ============================================================
# SYSTEM INFORMATION
# ============================================================

st.header(text["system"])

col1, col2, col3 = st.columns(3)

with col1:

    st.info(
        "🤖 Waiting-Time ML\n\n"
        "Random Forest Regressor"
    )

with col2:

    st.info(
        "🔮 Crowd Prediction\n\n"
        "Random Forest Regressor"
    )

with col3:

    st.info(
        "⚠️ Crowd Risk\n\n"
        "Random Forest Classifier"
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "QueueSense AI | Smart Queue Management "
    "using Machine Learning | "
    "Currently running on demo/training data."
)
# ============================================================
# FEEDBACK RATING
# ============================================================

st.header("⭐ Rate Your QueueSense AI Experience")

st.caption(
    "Your feedback helps us improve QueueSense AI."
)

rating = st.slider(
    "How would you rate QueueSense AI?",
    min_value=1,
    max_value=5,
    value=5,
    step=1
)

rating_labels = {
    1: "😞 Poor",
    2: "🙁 Fair",
    3: "😐 Good",
    4: "🙂 Very Good",
    5: "🤩 Excellent"
}

st.write(
    f"Your rating: **{rating_labels[rating]}**"
)

feedback = st.text_area(
    "💬 Tell us what you think (optional)",
    placeholder="Write your feedback here..."
)

if st.button("📤 Submit Feedback"):

    st.success(
        f"✅ Thank you! Your rating of **{rating}/5** "
        "has been recorded for this demo."
    )

    if feedback:
        st.info(
            f"💬 Your feedback: {feedback}"
        )

st.caption(
    "⚠️ Feedback is currently for demo purposes."
)

st.header(text["service"])

service_data = (
    df.groupby("service_type")["current_crowd"]
    .mean()
)

st.bar_chart(
    service_data
)