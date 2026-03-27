import os
import requests
import json
import datetime
import streamlit as st
from litellm import completion

# --- 1. WARM & WELCOMING DESIGN ---
st.set_page_config(page_title="Vedic AI Astrologer", page_icon="🪔", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFDF8; }
    h1, h2, h3, p, div, span, li, label { color: #3E2723 !important; }
    [data-testid="stChatMessage"] {
        background-color: #FFF2D7;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #F5DEB3;
    }
    .stButton>button { 
        background-color: #D2691E !important; 
        color: white !important; 
        border-radius: 15px; 
        width: 100%;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover { background-color: #A0522D !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. SECRETS SETUP ---
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
ASTRO_API_KEY = st.secrets.get("ASTRO_API_KEY", "YOUR_API_KEY")

# --- 3. MEMORY SETUP ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "math_data" not in st.session_state:
    st.session_state.math_data = None
if "dob_string" not in st.session_state:
    st.session_state.dob_string = None

# --- 4. NEW: AUTO-LOCATION (GEOCODING) ---
def get_coordinates(city_name):
    """Translates a city name into Latitude and Longitude using OpenStreetMap."""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        # We must include a User-Agent so they know who is pinging their free server
        headers = {"User-Agent": "VedicAIAstrologerApp/1.0"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200 and len(response.json()) > 0:
            data = response.json()[0]
            return float(data["lat"]), float(data["lon"])
        else:
            return None, None
    except Exception:
        return None, None

# --- 5. UPGRADED: DEEP MATH LAYER (THE BIG FOUR CHARTS) ---
def get_astrology_data(day, month, year, hour, minute, lat, lon, tzone):
    """Fetches D1, D9, D10, and D7 charts for deep AI analysis"""
    headers = {
        "x-astrologyapi-key": ASTRO_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "day": day, "month": month, "year": year,
        "hour": hour, "min": minute, "lat": lat, "lon": lon, "tzone": tzone
    }
    
    try:
        # 1. The Foundations
        basic_res = requests.post("https://json.astrologyapi.com/v1/astro_details", headers=headers, json=data).json()
        planets_res = requests.post("https://json.astrologyapi.com/v1/planets", headers=headers, json=data).json()
        
        # 2. The Deep Divisional Charts
        d9_res = requests.post("https://json.astrologyapi.com/v1/horo_chart_info/D9", headers=headers, json=data).json()
        d10_res = requests.post("https://json.astrologyapi.com/v1/horo_chart_info/D10", headers=headers, json=data).json()
        d7_res = requests.post("https://json.astrologyapi.com/v1/horo_chart_info/D7", headers=headers, json=data).json()
        
        # Package everything into one master dictionary for Gemini
        return {
            "basic_details": basic_res,
            "d1_planetary_placements": planets_res,
            "d9_marriage_and_soul": d9_res,
            "d10_career_and_business": d10_res,
            "d7_children_and_creativity": d7_res
        }
    except Exception as e:
        return {"error": str(e)}
# --- 6. THE SIDEBAR (NOW WITH CITY SEARCH) ---
with st.sidebar:
    st.header("✨ Your Birth Details")
    
    col1, col2, col3 = st.columns(3)
    with col1: day = st.number_input("Day", min_value=1, max_value=31, value=15)
    with col2: month = st.number_input("Month", min_value=1, max_value=12, value=8)
    with col3: year = st.number_input("Year", min_value=1900, max_value=2100, value=1992)
    
    col4, col5 = st.columns(2)
    with col4: hour = st.number_input("Hour (0-23)", min_value=0, max_value=23, value=8)
    with col5: minute = st.number_input("Minute", min_value=0, max_value=59, value=15)
    
    # NEW: Simple text box instead of Latitude/Longitude math
    city_input = st.text_input("Birth City & State", placeholder="Jaipur, Rajasthan")
    tzone = st.number_input("Timezone (e.g., 5.5 for India)", value=5.5)
    
    if st.button("Save Details & Generate Chart"):
        if not city_input:
            st.warning("Please enter a city name.")
        else:
            with st.spinner("Finding coordinates & drawing deep charts..."):
                # 1. Translate the city to GPS coordinates
                lat, lon = get_coordinates(city_input)
                
                if lat is None:
                    st.error("Could not find coordinates for that city. Please try adding the state or country.")
                else:
                    # 2. Fetch the D1 and D9 math using the newly found coordinates
                    math_result = get_astrology_data(day, month, year, hour, minute, lat, lon, tzone)
                    
                    if "error" in math_result:
                        st.error(f"Math API Failed: {math_result['error']}")
                    else:
                        st.session_state.math_data = math_result
                        st.session_state.dob_string = f"{day}/{month}/{year}"
                        st.success(f"Location found! ({lat}, {lon}). Deep chart saved!")
                        
                        st.session_state.messages.append({
                            "role": "user", 
                            "content": "Hello! I have saved my birth details. Please show me a beautifully formatted summary of my Ascendant, Moon sign, Sun sign, and one interesting fact you notice in my D-9 Navamsha chart."
                        })

    st.divider()
    st.subheader("🔮 Ask About...")
    topics = [
        "Life Predictions", "Monthly Predictions", "Yogas & Doshas", 
        "Baby Names by Rashi", "Mahadasha Chart", "Career", 
        "Wealth & Finance", "Love & Married Life", "Mental Peace", "Legal & Compliance"
    ]
    
    for topic in topics:
        if st.button(topic):
            if st.session_state.math_data:
                st.session_state.messages.append({
                    "role": "user", 
                    "content": f"Based strictly on my verified D1 and Navamsha chart data, tell me about my {topic}. Please reference specific planets or houses if relevant."
                })
            else:
                st.warning("Please save your birth details first!")

# --- 7. THE MAIN CHAT INTERFACE ---
st.title("🪔 Your Personal Astrologer")
st.write("Welcome! Save your details to lock in your D1 and D9 charts, then ask me anything.")

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if user_input := st.chat_input("Ask a specific question about your chart..."):
    if st.session_state.math_data:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
    else:
        st.error("Please save your birth details in the sidebar first!")

# --- 8. THE AI LAYER (INTERPRETER) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Consulting the stars..."):
            
            current_date = datetime.datetime.now().strftime("%B %Y")
            
            # The AI prompt is now aware it has access to both D1 and D9
            system_context = f"""
            You are a warm, empathetic, and highly accurate Vedic astrologer. 
            The user's Date of Birth is: {st.session_state.dob_string}
            
            Here is their complete, mathematically verified astrological data (including D1 planets and D9 Navamsha houses):
            {json.dumps(st.session_state.math_data)}
            
            RULES:
            1. Base their core placements strictly on the JSON data provided.
            2. You now have access to their Navamsha (D9) chart data. Use it to provide deeper insights, especially for questions about marriage, soul purpose, or hidden strengths.
            3. The current date is {current_date}. If asked for predictions, use your internal knowledge of current planetary transits.
            """
            
            api_messages = [{"role": "system", "content": system_context}]
            api_messages.extend(st.session_state.messages) 
            
            try:
                response = completion(
                    model="gemini/gemini-2.5-flash", 
                    messages=api_messages
                )
                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as e:
                st.error(f"Connection Error: {e}")
