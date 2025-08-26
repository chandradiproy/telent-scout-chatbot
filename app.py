# app.py

import streamlit as st
import time
from src.chatbot.core import Chatbot

# --- Page Configuration ---
st.set_page_config(
    page_title="TalentScout AI",
    page_icon="🤖",
    layout="centered",
)

# --- Session State Initialization ---
def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add the initial greeting from the chatbot
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Hello! I'm an intelligent Hiring Assistant from TalentScout. I'm here to ask you a few questions to get started. What is your full name?"
            }
        )
    if "conversation_stage" not in st.session_state:
        st.session_state.conversation_stage = "get_name"
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info = {}
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = Chatbot()

# --- Main Application ---
def main():
    """Main function to run the Streamlit chatbot application."""
    st.title("🤖 TalentScout AI Hiring Assistant")
    st.write("---")

    initialize_session_state()

    # --- Display Chat History ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- Handle User Input ---
    if st.session_state.conversation_stage != "end":
        if prompt := st.chat_input("Your response..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # --- Assistant's Response ---
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    chatbot_instance = st.session_state.chatbot
                    assistant_response = chatbot_instance.handle_response(prompt)
                    
                    # Simulate stream of response for better UX
                    message_placeholder = st.empty()
                    full_response = ""
                    for chunk in assistant_response.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.info("This conversation has ended. Thank you for your time!")


if __name__ == "__main__":
    main()
