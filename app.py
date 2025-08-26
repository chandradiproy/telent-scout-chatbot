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

    # --- Sidebar for Controls ---
    st.sidebar.title("Controls")
    if st.sidebar.button("Start Over"):
        st.session_state.clear()
        st.rerun()

    initialize_session_state()

    # --- Display Chat History with Avatars ---
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "🧑‍💻"
        with st.chat_message(message["role"], avatar=avatar):
            # To render newlines correctly in Streamlit's markdown,
            # replace single newlines with two spaces followed by a newline.
            st.markdown(message["content"].replace('\n', '  \n'))

    # --- Handle User Input ---
    if st.session_state.conversation_stage != "end":
        if prompt := st.chat_input("Your response..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    chatbot_instance = st.session_state.chatbot
                    assistant_response = chatbot_instance.handle_response(prompt)
                    
                    # --- BUG FIX: Simplified Streaming Logic ---
                    # This new logic streams character by character to reliably handle newlines.
                    message_placeholder = st.empty()
                    full_response = ""
                    for char in assistant_response:
                        full_response += char
                        time.sleep(0.01) # A shorter sleep time for smoother character streaming
                        # Correctly render newlines during the stream
                        message_placeholder.markdown(full_response.replace('\n', '  \n') + "▌")
                    # Display the final, complete response without the cursor
                    message_placeholder.markdown(full_response.replace('\n', '  \n'))
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.info("This conversation has ended. Thank you for your time! You can start a new conversation by clicking the 'Start Over' button in the sidebar.")


if __name__ == "__main__":
    main()
