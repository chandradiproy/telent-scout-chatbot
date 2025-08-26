# src/chatbot/core.py

import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import json
from datetime import datetime

from src.prompts import templates
from src.utils import helpers

# --- Environment and API Initialization ---
def initialize_api():
    """Loads environment variables and initializes the Groq client."""
    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.error("GROQ_API_KEY not found. Please set it in your .env file.")
        st.stop()
    return Groq(api_key=groq_api_key)

CLIENT = initialize_api()
CANDIDATE_DATA_FILE = "candidate_data.json"

# --- Conversation Management ---
class Chatbot:
    """Handles the chatbot's conversation logic and state."""

    def __init__(self):
        self.conversation_stages = [
            ("get_name", "This is unused."),
            ("get_email", "Great, thank you. What is your email address?"),
            ("get_phone", "Thanks. What is your phone number?"),
            ("get_experience", "Perfect. How many years of professional experience do you have?"),
            ("get_position", "Understood. What position or positions are you interested in?"),
            ("get_location", "Noted. What is your current location? (e.g., City, Country)"),
            ("get_tech_stack", "Excellent. Could you please list your primary tech stack? (e.g., Python, React, AWS)"),
            ("tech_questions_generated", self._generate_tech_questions),
            ("tech_answers_provided", self._score_answers),
            ("scoring_done", "This is unused."),
        ]

    def _get_next_stage(self, current_stage_name):
        """Finds the next stage in the conversation flow."""
        for i, (stage_name, _) in enumerate(self.conversation_stages):
            if stage_name == current_stage_name:
                if i + 1 < len(self.conversation_stages):
                    return self.conversation_stages[i + 1]
        return None, None

    def _call_llm(self, prompt, model="llama3-8b-8192", temperature=0.5):
        """Helper function to make a call to the Groq API."""
        try:
            chat_completion = CLIENT.chat.completions.create(
                messages=[
                    {"role": "system", "content": templates.get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                model=model,
                temperature=temperature,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"An API error occurred: {e}")
            return None

    def _detect_intent(self, user_prompt, current_stage):
        """Detects the user's intent using the LLM."""
        prompt = templates.get_intent_detection_prompt(user_prompt, current_stage)
        intent = self._call_llm(prompt, model="llama3-8b-8192", temperature=0)
        return intent

    def handle_response(self, user_prompt: str):
        """Processes the user's response based on intent and conversation stage."""
        current_stage = st.session_state.get("conversation_stage", "get_name")

        if user_prompt.lower() in ["exit", "quit", "bye"]:
            st.session_state.conversation_stage = "end"
            return "Thank you for your time. Have a great day!"

        if current_stage == "tech_questions_generated":
            intent = self._detect_intent(user_prompt, current_stage)
            is_likely_not_an_answer = len(user_prompt.split()) < 15

            if intent == "ANSWERING_QUESTION" and not is_likely_not_an_answer:
                st.session_state.candidate_info['tech_question_answers'] = user_prompt
                st.session_state.conversation_stage = "tech_answers_provided"
                return self._score_answers()
            else:
                return "My purpose is to collect your answers to the questions provided. Please provide a detailed response for each question to proceed."

        if current_stage.startswith("get_"):
            field_name = current_stage.split("get_")[1]
            if field_name == "email" and not helpers.is_valid_email(user_prompt):
                return "That doesn't look like a valid email address. Could you please try again?"
            st.session_state.candidate_info[field_name] = user_prompt
        
        next_stage, next_response_or_func = self._get_next_stage(current_stage)
        if next_stage:
            st.session_state.conversation_stage = next_stage
            if callable(next_response_or_func):
                return next_response_or_func()
            return next_response_or_func

        return "Thank you. A recruiter will be in touch shortly."

    def _generate_tech_questions(self):
        """Generates technical questions and instructs the user on how to answer."""
        tech_stack = st.session_state.candidate_info.get("tech_stack", "general software development")
        experience = st.session_state.candidate_info.get("experience", "0")
        prompt = templates.get_tech_questions_prompt(tech_stack, experience)
        questions = self._call_llm(prompt)
        
        if questions:
            st.session_state.candidate_info['tech_questions_asked'] = questions
            response = (
                f"Great, thank you. Here are a few technical questions for you:\n\n---\n\n{questions}\n\n---\n\n"
                "Please answer each question clearly. You can number your answers (e.g., 1., 2., etc.) to correspond with the questions."
            )
            st.session_state.conversation_stage = "tech_questions_generated"
            return response
        else:
            st.session_state.conversation_stage = "scoring_done"
            return "I'm having trouble generating questions right now. A recruiter will be in touch."

    def _save_results_to_json_file(self, score_data):
        """Saves the complete candidate profile to a JSON file, appending to existing data."""
        st.session_state.candidate_info['score_feedback'] = score_data
        st.session_state.candidate_info['interview_timestamp'] = datetime.now().isoformat()
        
        try:
            # Read existing data from the file
            if os.path.exists(CANDIDATE_DATA_FILE) and os.path.getsize(CANDIDATE_DATA_FILE) > 0:
                with open(CANDIDATE_DATA_FILE, "r") as f:
                    all_candidates_data = json.load(f)
            else:
                all_candidates_data = []
        except (json.JSONDecodeError, FileNotFoundError):
            all_candidates_data = []

        # Append new candidate data
        all_candidates_data.append(st.session_state.candidate_info)

        # Write all data back to the file
        with open(CANDIDATE_DATA_FILE, "w") as f:
            json.dump(all_candidates_data, f, indent=4)
        
        st.toast("Candidate data saved successfully!")

    def _score_answers(self):
        """Scores the candidate's answers, parses the JSON, and saves the results."""
        questions = st.session_state.candidate_info.get('tech_questions_asked')
        answers = st.session_state.candidate_info.get('tech_question_answers')
        
        if not questions or not answers:
            return "Something went wrong. A recruiter will be in touch."

        prompt = templates.get_scoring_prompt(questions, answers)
        with st.spinner("Evaluating your answers..."):
            score_response = self._call_llm(prompt, model="llama3-70b-8192", temperature=0.1)
        
        st.session_state.conversation_stage = "end"

        if score_response:
            try:
                # The primary change: parse the LLM's string response into a Python dict
                score_data = json.loads(score_response)
                self._save_results_to_json_file(score_data)
                return "Thank you for your responses. That's all the information I need for now. A recruiter from TalentScout will review your details and get in touch with you soon. Have a great day!"
            except json.JSONDecodeError:
                # Fallback if the LLM fails to return valid JSON
                self._save_results_to_json_file({"error": "Failed to parse score JSON.", "raw_response": score_response})
                return "Your answers have been saved, but there was an issue with the automated evaluation. A recruiter will review them manually. Thank you for your time."
        else:
            self._save_results_to_json_file({"error": "Failed to generate score."})
            return "I'm having trouble evaluating the answers right now, but they have been saved. A recruiter will review them manually. Thank you for your time."
