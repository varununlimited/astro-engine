import os
import streamlit as st
from litellm import completion

# --- 1. WARM & WELCOMING DESIGN ---
st.set_page_config(page_title="Vedic AI Astrologer", page_icon="🪔", layout="wide")

st.markdown("""
    <style>
    /* Warm cream background */
    .stApp { background-color: #FFFDF8; }
    
    /* Force ALL text to be a dark, readable brown */
    h1, h2, h3, p, div, span, li, label { 
        color: #3E2723 !important; 
    }
    
    /* Style the chat bubbles to stand out */
    [data-testid="stChatMessage"] {
        background-color: #FFF2D7;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #F5DEB3;
    }
    
    /* Styling the buttons to look like smooth, golden pills */
    .stButton>button { 
        background-color: #D2691E !important; 
        color: white !important; 
        border-radius: 15px; 
        width: 100%;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover { 
        background-color: #A0522D !important; 
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. API SETUP & MEMORY ---
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# Create a memory bank so the chatbot remembers the conversation
if "messages" not in st.session_state:
    st.session_state.messages = []
if "birth_info" not in st.session_state:
    st.session_state.birth_info = None

# --- 3. THE SIDEBAR (INPUTS & BUTTONS) ---
with st.sidebar:
    st.header("✨ Your Birth Details")
    
    dob = st.text_input("Date of Birth", placeholder="15 Aug 1992")
    time_birth = st.text_input("Time of Birth", placeholder="08:15 AM")
    place_birth = st.text_input("Place of Birth", placeholder="Jaipur, Rajasthan")
    
    if st.button("Save Details & Generate Chart"):
        if dob and time_birth and place_birth:
            st.session_state.birth_info = f"DOB: {dob}, Time: {time_birth}, Place: {place_birth}"
            # Automatically ask the AI for the basic chart
            st.session_state.messages.append({
                "role": "user", 
                "content": "Hello! Please show me a formatted table of my basic birth chart (Ascendant, Sun, Moon, etc.)."
            })
        else:
            st.warning("Please enter all birth details first.")

    st.divider()
    st.subheader("🔮 Ask About...")
    
    # Quick action buttons for the user
    topics = [
        "Life Predictions", "Monthly Predictions", "Yogas & Doshas", 
        "Baby Names by Rashi", "Mahadasha Chart", "Career", 
        "Wealth & Finance", "Love & Married Life", "Mental Peace", "Legal & Compliance"
    ]
    
    for topic in topics:
        if st.button(topic):
            if st.session_state.birth_info:
                st.session_state.messages.append({
                    "role": "user", 
                    "content": f"Based on my chart, tell me about my {topic}."
                })
            else:
                st.warning("Please save your birth details first!")

# --- 4. THE MAIN CHAT INTERFACE ---
st.title("🪔 Your Personal Astrologer")
st.write("Welcome! Save your details in the sidebar to reveal your chart, then ask me anything or use the quick buttons.")

# Display all chat messages on the screen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle custom questions typed into the bottom chat box
if user_input := st.chat_input("Ask a specific question about your chart..."):
    if st.session_state.birth_info:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
    else:
        st.error("Please save your birth details in the sidebar first!")

# --- 5. GENERATE AI RESPONSE ---
# If the last message in memory is from the user, the AI needs to reply
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Consulting the stars..."):
            
            # Package the birth info and chat history for the AI
            system_context = f"You are a warm, empathetic expert in Vedic astrology. The user's birth data is: {st.session_state.birth_info}."
            api_messages = [{"role": "system", "content": system_context}]
            api_messages.extend(st.session_state.messages) 
            
            try:
                response = completion(
                    model="gemini/gemini-2.5-flash", 
                    messages=api_messages
                )
                ai_reply = response.choices[0].message.content
                st.markdown(ai_reply)
                
                # Save the reply to memory
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            except Exception as e:
                st.error(f"Connection Error: {e}")
