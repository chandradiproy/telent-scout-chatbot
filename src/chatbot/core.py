# src/chatbot/core.py
import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

from src.prompts import templates
from src.utils import helpers

def initialize_api():
    """
    Loads environment variables and initializes the Groq API client.
    """
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found in environment variables.")
        st.stop()
    return Groq(api_key=groq_api_key)

CLIENT = initialize_api()

class Chatbot:
    def __init__(self):
        self.conversation_stages = [
            ("get_name", "Great, thank you. What is your email address?"),
            ("get_email", "Thanks. What is your phone number?"),
            ("get_phone", "Perfect. How many years of professional experience do you have?"),
            ("get_experience", "Understood. What position or positions are you interested in?"),
            ("get_position", "Noted. What is your current location? (e.g., City, Country)"),
            ("get_location", "Excellent. Could you please list your primary tech stack? (e.g., Python, React, AWS)"),
            ("get_tech_stack", self._generate_tech_questions),
            ("tech_questions_done", "Thank you for your responses. That's all the information I need for now. A recruiter from TalentScout will review your details and get in touch with you soon. Have a great day!"),
        ]
    
    def _get_next_stage(self, current_stage_name):
        """ Finds the next stage in the conversation flow. """
        
        for i, (stage_name, _) in enumerate(self.conversation_stages):
            if stage_name == current_stage_name:
                if i+1 < len(self.conversation_stages):
                    return self.conversation_stages[i+1]
        return None, None # End of conversation
    
    def handle_response(self, user_prompt: str):
        """ Processes the user's response based on the current conversation stage. """
        current_stage_name = st.session_state.get('conversation_stage', 'get_name')
        if user_prompt.lower() in ['exit','quit','stop','bye','goodbye','see you']:
            st.session_state.conversation_stage = "end"
            return "Thank you for your time. Have a great day!"
        
        # --- Process Information Gathering Stages ---
        if current_stage_name.startswith("get_"):
            field_name = current_stage_name.split("get_")[1]
            
            # --- Validate email ---
            if field_name == "email" and not helpers.is_valid_email(user_prompt):
                return "That doesn't look like a valid email address. Could you please try again?"
            
            st.session_state.candidate_info[field_name] = user_prompt
            next_stage, next_response_or_func = self._get_next_stage(current_stage_name)
            
            if next_stage:
                st.session_state.conversation_stage = next_stage
                if callable(next_response_or_func):
                    return next_response_or_func()
                return next_response_or_func
        elif current_stage_name == "tech_questions_done":
            next_stage, next_response = self._get_next_stage(current_stage_name)
            if next_stage:
                st.session_state.conversation_stage = next_stage
                return next_response
        return "I'm sorry, I'm not sure how to respond to that. Let's continue."
    
    def _generate_tech_questions(self):
        """
        Calls the LLM to generate technical questions and presents them.
        """
        tech_stack = st.session_state.candidate_info.get("tech_stack","general software development")
        prompt = templates.get_tech_questions_prompt(tech_stack=tech_stack)
        
        try:
            chat_completion = CLIENT.chat.completions.create(
                messages=[
                    {"role":"system", "content": templates.get_system_prompt()},
                    {"role":"user","conent":prompt}
                ],
                model="llama3-8b-8192",
                temperature=0.2,
            )
            questions = chat_completion.choices[0].message.content
            response = f"Great, thank you for providing your tech stack. Here are a few technical questions for you:\n\n---\n\n{questions}\n\n---\n\nPlease take your time to answer them."
            st.session_state.conversation_stage = "tech_questions_done"
            return response
        except Exception as e:
            st.error(f"Error generating technical questions: {e}")
            return "I encountered an error while generating technical questions. Let's proceed to the next step."
    