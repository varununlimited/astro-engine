import os
import streamlit as st
from litellm import completion

# --- 1. PAGE SETUP ---
# This configures the browser tab title and icon
st.set_page_config(page_title="AI Astrologer", page_icon="✨")

# --- 2. SET YOUR API KEY ---
# Streamlit will securely inject the key from its hidden settings later
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
# --- 3. THE USER INTERFACE ---
st.title("🌟 AI Astrology Engine")
st.write("Enter your birth details below to generate a highly accurate, AI-powered consensus reading.")

# Create clean input boxes for the user
dob = st.text_input("Date of Birth", placeholder="e.g., August 15, 1992")
time_of_birth = st.text_input("Time of Birth", placeholder="e.g., 08:15 AM")
place_of_birth = st.text_input(
    "Place of Birth", placeholder="e.g., Jaipur, Rajasthan, India")

# --- 4. THE BUTTON & LOGIC ---
# Everything indented under this button only happens AFTER the user clicks it
if st.button("Generate Reading ✨"):

    # Check if they left any boxes blank
    if not dob or not time_of_birth or not place_of_birth:
        st.warning("⚠️ Please fill in all three fields before generating!")
    else:
        # Show a spinning loading wheel while the AI thinks
        with st.spinner("Calculating planetary alignments... this takes a few seconds..."):

            prompt = f"""
            You are an expert in Vedic astrology. 
            First, determine the exact latitude and longitude for: {place_of_birth}.
            Using those coordinates, generate a concise birth chart reading 
            for a person born on {dob} at {time_of_birth}. 
            Focus on the Ascendant, Moon sign, and Sun sign.
            """

            try:
                response = completion(
                    model="gemini/gemini-2.5-flash",
                    messages=[{"role": "user", "content": prompt}]
                )

                # --- 5. DISPLAY THE RESULTS ---
                st.success("Reading Complete!")
                st.markdown("### Your Birth Chart Analysis")
                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(f"❌ Connection Error: {e}")
