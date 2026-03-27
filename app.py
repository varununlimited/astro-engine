import os
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

# --- 2. API SETUP ---
# We only need Gemini now. No more third-party math APIs to crash!
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# --- 3. MEMORY SETUP ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "verified_chart" not in st.session_state:
    st.session_state.verified_chart = None

# --- 4. THE SIDEBAR (FOOLPROOF INPUTS) ---
with st.sidebar:
    st.header("✨ Your Core Signs")
    st.write("Select your placements below to lock in an accurate reading and prevent AI guesswork.")
    
    zodiac_signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    ascendant = st.selectbox("Lagna (Ascendant)", zodiac_signs)
    moon_sign = st.selectbox("Rashi (Moon Sign)", zodiac_signs)
    sun_sign = st.selectbox("Sun Sign", zodiac_signs)
    
    if st.button("Save Details & Start Chat"):
        # Save the exact signs to the app's memory
        st.session_state.verified_chart = f"Ascendant: {ascendant}, Moon Sign: {moon_sign}, Sun Sign: {sun_sign}"
        st.success("Signs saved securely!")
        
        # Automatically start the conversation
        st.session_state.messages.append({
            "role": "user", 
            "content": "Hello! I have saved my signs. Please give me a warm welcome and a brief summary of my core personality based on these 3 signs."
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
            if st.session_state.verified_chart:
                st.session_state.messages.append({
                    "role": "user", 
                    "content": f"Based strictly on my verified signs ({st.session_state.verified_chart}), tell me about my {topic}."
                })
            else:
                st.warning("Please click 'Save Details' first!")

# --- 5. THE MAIN CHAT INTERFACE ---
st.title("🪔 Your Personal Astrologer")
st.write("Welcome! Save your signs in the sidebar to lock in your chart, then ask me anything or use the quick buttons.")

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Handle text box input at the bottom
if user_input := st.chat_input("Ask a specific question about your chart..."):
    if st.session_state.verified_chart:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
    else:
        st.error("Please save your details in the sidebar first!")

# --- 6. THE AI LAYER (INTERPRETER) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Consulting the stars..."):
            
            # THE MAGIC: We force Gemini to only look at the exact signs the user picked
            system_context = f"""
            You are a warm, empathetic, and highly accurate Vedic astrologer. 
            Do NOT hallucinate or guess planetary positions. 
            Base all your answers STRICTLY on these known facts about the user: 
            {st.session_state.verified_chart}
            If you need more info to answer a question (like exact degrees or house placements), politely explain that you are giving a general reading based on their core signs.
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
