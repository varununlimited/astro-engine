import os
import streamlit as st
from litellm import completion

# --- 1. WARM & WELCOMING DESIGN ---
# Setting a wide layout and a mystical icon
st.set_page_config(page_title="Vedic AI Astrologer", page_icon="🪔", layout="wide")

# Injecting Custom CSS to create a warm, inviting color palette
st.markdown("""
    <style>
    /* Warm cream background and dark maroon text */
    .stApp { background-color: #FFFDF8; }
    h1, h2, h3 { color: #8B4513; }
    
    /* Styling the buttons to look like smooth, golden pills */
    .stButton>button { 
        background-color: #D2691E; 
        color: white; 
        border-radius: 15px; 
        width: 100%;
        border: none;
    }
    .stButton>button:hover { background-color: #A0522D; }
    </style>
""", unsafe_allow_html=True)

# --- 2. API SETUP & MEMORY (SESSION STATE) ---
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# This creates a "memory" bank so the chatbot remembers the conversation
if "messages" not in st.session_state:
    st.session_state.messages = []
if "birth_info" not in st.session_state:
    st.session_state.birth_info = None

# --- 3. THE SIDEBAR (INPUTS & QUICK BUTTONS) ---
with st.sidebar:
    st.header("✨ Your Birth Details")
    
    dob = st.text_input("Date of Birth", placeholder="15 Aug 1992")
    time_birth = st.text_input("Time of Birth", placeholder="08:15 AM")
    place_birth = st.text_input("Place of Birth", placeholder="Jaipur, Rajasthan")
    
    if st.button("Save Details & Generate Chart"):
        if dob and time_birth and place_birth:
            # Save the details to the app's memory
            st.session_state.birth_info = f"DOB: {dob}, Time: {time_birth}, Place: {place_birth}"
            
            # Create a hidden prompt to generate the basic chart table
            chart_prompt = f"Using this birth data ({st.session_state.birth_info}), act as a welcoming Vedic astrologer. First, warmly greet the user. Then, provide a clear, formatted Markdown table showing their basic planetary placements (Ascendant, Sun, Moon, etc.)."
            
            # Add the user's hidden request and the AI's response to the chat history
            st.session_state.messages.append({"role": "user", "content": "Show me my basic birth chart."})
            
            with st.spinner("Drawing your chart..."):
                try:
                    response = completion(
                        model="gemini/gemini-2.5-flash", 
                        messages=[{"role": "system", "content": chart_prompt}]
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        else:
            st.warning("Please enter all birth details first.")

    st.divider()
    
    # --- QUICK ACTION BUTTONS ---
    st.subheader("🔮 Ask About...")
    
    # We create a list of all your requested buttons
    topics = [
        "Life Predictions", "Monthly Predictions", "Yogas & Doshas", 
        "Baby Names by Rashi", "Mahadasha Chart", "Career", 
        "Wealth & Finance", "Love & Married Life", "Mental Peace", "Legal & Compliance"
    ]
    
    # This loops through the list and creates a clickable button for each one
    for topic in topics:
        if st.button(topic):
            if st.session_state.birth_info:
                # If they click a button, we automatically send that question to the chat!
                auto_question = f"Based on my chart, tell me about my {topic}."
                st.session_state.messages.append({"role": "user", "content": auto_question})
            else:
                st.warning("Please save your birth details at the top first!")

# --- 4. THE MAIN CHAT INTERFACE ---
st.title("🪔 Your Personal Astrologer")
st.write("Welcome. Save your details in the sidebar to reveal your chart, then ask me anything or use the quick buttons.")

# Display all previous chat messages stored in memory
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. HANDLING NEW CHAT MESSAGES ---
# We check if the last message in memory was from the user. If it was, the AI needs to reply!
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    
    # Only run the AI if the very last message is a user question that hasn't been answered yet
    if len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] != "user":
        
        with st.chat_message("assistant"):
            with st.spinner("Consulting the stars..."):
                
                # We package up the user's birth info AND their whole chat history to send to Gemini
                system_context = f"You are a warm, empathetic expert in Vedic astrology. The user's birth data is: {st.session_state.birth_info}."
                
                # Prepare the message format LiteLLM expects
                api_messages = [{"role": "system", "content": system_context}]
                api_messages.extend(st.session_state.messages) 
                
                try:
                    response = completion(
                        model="gemini/gemini-2.5-flash", 
                        messages=api_messages
                    )
                    ai_reply = response.choices[0].message.content
                    st.markdown(ai_reply)
                    
                    # Save the AI's reply to memory so it stays on screen
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# This allows the user to type custom questions freely
if user_text := st.chat_input("Ask a specific question about your chart..."):
    if st.session_state.birth_info:
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.rerun() # This instantly refreshes the page to show their new message
    else:
        st.error("Please save your birth details in the sidebar first!")
