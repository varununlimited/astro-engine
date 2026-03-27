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

# --- 4. THE MATH LAYER (API CALL) ---
def get_astrology_data(day, month, year, hour, minute, lat, lon, tzone):
    url = "https://json.astrologyapi.com/v1/astro_details"
    headers = {
        "x-astrologyapi-key": ASTRO_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "day": day, "month": month, "year": year,
        "hour": hour, "min": minute, "lat": lat, "lon": lon, "tzone": tzone
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

# --- 5. THE SIDEBAR ---
with st.sidebar:
    st.header("✨ Your Birth Details")
    st.write("Enter exact details for mathematical precision.")
    
    col1, col2, col3 = st.columns(3)
    with col1: day = st.number_input("Day", min_value=1, max_value=31, value=15)
    with col2: month = st.number_input("Month", min_value=1, max_value=12, value=8)
    with col3: year = st.number_input("Year", min_value=1900, max_value=2100, value=1992)
    
    col4, col5 = st.columns(2)
    with col4: hour = st.number_input("Hour (0-23)", min_value=0, max_value=23, value=8)
    with col5: minute = st.number_input("Minute", min_value=0, max_value=59, value=15)
    
    st.write("Location Coordinates ([Find Here](https://www.latlong.net/))")
    col6, col7 = st.columns(2)
    with col6: lat = st.number_input("Latitude", value=26.9124)
    with col7: lon = st.number_input("Longitude", value=75.7873)
    tzone = st.number_input("Timezone", value=5.5)
    
    if st.button("Save Details & Generate Chart"):
        with st.spinner("Calculating exact planetary positions..."):
            math_result = get_astrology_data(day, month, year, hour, minute, lat, lon, tzone)
            
            if "error" in math_result:
                st.error(f"Math API Failed: {math_result['error']}")
            else:
                st.session_state.math_data = math_result
                st.session_state.dob_string = f"{day}/{month}/{year}" # Saving the exact DOB for the AI
                st.success("Mathematical chart saved!")
                
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "Hello! I have saved my birth details. Please show me a beautifully formatted summary of my exact Ascendant, Moon sign, and Sun sign."
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
                    "content": f"Based strictly on my verified chart data, tell me about my {topic}."
                })
            else:
                st.warning("Please save your birth details first!")

# --- 6. THE MAIN CHAT INTERFACE ---
st.title("🪔 Your Personal Astrologer")
st.write("Welcome! Save your details to lock in your mathematical chart, then ask me anything.")

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

# --- 7. THE AI LAYER (INTERPRETER) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Consulting the stars..."):
            
            # We grab today's exact date to feed to the AI
            current_date = datetime.datetime.now().strftime("%B %Y")
            
            # The new, smarter instructions
            system_context = f"""
            You are a warm, empathetic, and highly accurate Vedic astrologer. 
            The user's Date of Birth is: {st.session_state.dob_string}
            
            Here is their mathematically verified natal chart data:
            {json.dumps(st.session_state.math_data)}
            
            RULES:
            1. Base their core placements (Ascendant, Moon, Nakshatra) STRICTLY on the JSON data provided.
            2. If the Sun sign is not explicitly labeled in the JSON, use their Date of Birth to accurately state their Vedic Sun sign.
            3. The current date is {current_date}. If asked for monthly predictions, life predictions, or transits, you have full permission to use your internal knowledge of current planetary transits and apply them to the user's natal chart. Do not refuse to give predictions.
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
