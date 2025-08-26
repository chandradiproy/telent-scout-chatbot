# src/chatbot/core.py

import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import json
import re
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
            ("get_language", "This is a placeholder as the first real question is for the name."),
            ("get_name", "Ask for the user's full name."),
            ("get_email", "Ask for the user's email address."),
            ("get_phone", "Ask for the user's phone number."),
            ("get_experience", "Ask for the user's years of professional experience."),
            ("get_position", "Ask for the position they are interested in."),
            ("get_location", "Ask for their current location."),
            ("get_tech_stack", "Ask them to list their primary tech stack."),
            ("tech_questions_generated", self._generate_tech_questions),
            ("tech_answers_provided", self._score_answers),
            ("scoring_done", "This is unused."),
        ]

    def _get_stage_instruction(self, stage_name):
        """Finds the instruction for a given stage."""
        for name, instruction in self.conversation_stages:
            if name == stage_name:
                return instruction
        return None

    def _call_llm(self, prompt, model="llama3-8b-8192", temperature=0.7, json_only=False):
        """Helper function to make a call to the Groq API, now language-aware."""
        language = st.session_state.candidate_info.get("language", "English")
        
        try:
            chat_completion = CLIENT.chat.completions.create(
                messages=[
                    {"role": "system", "content": templates.get_system_prompt(language)},
                    {"role": "user", "content": prompt},
                ],
                model=model,
                temperature=temperature,
            )
            response_text = chat_completion.choices[0].message.content.strip()

            if json_only:
                json_match = re.search(r'```(json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    return json_match.group(2)
                else:
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        return json_match.group(0)
                return None
            
            return response_text

        except Exception as e:
            st.error(f"An API error occurred: {e}")
            return None

    def _detect_intent(self, user_prompt, current_stage):
        """Detects the user's intent using the LLM."""
        prompt = templates.get_intent_detection_prompt(user_prompt, current_stage)
        intent = self._call_llm(prompt, model="llama3-8b-8192", temperature=0)
        return intent

    def handle_response(self, user_prompt: str):
        """Processes the user's response with a more robust state machine."""
        current_stage = st.session_state.get("conversation_stage", "get_language")

        if user_prompt.lower() in ["exit", "quit", "bye"]:
            st.session_state.conversation_stage = "end"
            return "Thank you for your time. Have a great day!"

        # --- More explicit state handling and validation logic ---
        if current_stage == "get_language":
            st.session_state.candidate_info['language'] = user_prompt
        elif current_stage == "get_name":
            st.session_state.candidate_info['name'] = user_prompt
        elif current_stage == "get_email":
            if not helpers.is_valid_email(user_prompt):
                return self._call_llm("The user provided an invalid email. Politely ask them to provide a valid one.")
            st.session_state.candidate_info['email'] = user_prompt
        elif current_stage.startswith("get_"):
            field_name = current_stage.split("get_")[1]
            st.session_state.candidate_info[field_name] = user_prompt
        
        elif current_stage == "tech_questions_generated":
            intent = self._detect_intent(user_prompt, current_stage)
            is_likely_not_an_answer = len(user_prompt.split()) < 15

            if intent == "ANSWERING_QUESTION" and not is_likely_not_an_answer:
                st.session_state.candidate_info['tech_question_answers'] = user_prompt
                st.session_state.conversation_stage = "tech_answers_provided"
                return self._score_answers()
            else:
                # BUG FIX: Use a much more direct and simple instruction.
                evasion_instruction = "Your purpose is to get answers to the questions. Please state that you cannot regenerate questions and ask the user to answer the ones provided so you can proceed."
                return self._call_llm(evasion_instruction)

        # Now, find the NEXT stage and get its instruction.
        next_stage_index = [i for i, (name, _) in enumerate(self.conversation_stages) if name == current_stage][0] + 1
        if next_stage_index < len(self.conversation_stages):
            next_stage_name, next_instruction = self.conversation_stages[next_stage_index]
            st.session_state.conversation_stage = next_stage_name
            
            if callable(next_instruction):
                return next_instruction()
            else:
                return self._call_llm(next_instruction)

        return self._call_llm("The interview is complete. Thank the user and end the conversation.")


    def _generate_tech_questions(self):
        """Generates technical questions tailored to the candidate's experience."""
        tech_stack = st.session_state.candidate_info.get("tech_stack", "general software development")
        experience = st.session_state.candidate_info.get("experience", "1")
        
        prompt = templates.get_tech_questions_prompt(tech_stack, experience)
        questions = self._call_llm(prompt, temperature=0.6)
        
        if questions:
            st.session_state.candidate_info['tech_questions_asked'] = questions
            instruction = (
                f"You have generated the following questions:\n---\n{questions}\n---\n"
                "Now, present these questions to the user. Start by saying 'Great, thank you. Based on your experience, here are a few technical questions for you:'. "
                "Then, list the questions. Finally, instruct them to answer each question clearly and that they can number their answers."
            )
            st.session_state.conversation_stage = "tech_questions_generated"
            return self._call_llm(instruction)
        else:
            st.session_state.conversation_stage = "scoring_done"
            return self._call_llm("I'm having trouble generating questions right now. Apologize and say a recruiter will be in touch.")

    def _save_results_to_json_file(self, score_data):
        """Performs sentiment analysis and saves the complete candidate profile to a JSON file."""
        conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        sentiment_prompt = templates.get_sentiment_analysis_prompt(conversation_history)
        sentiment_response = self._call_llm(sentiment_prompt, temperature=0.1, json_only=True)
        
        try:
            sentiment_data = json.loads(sentiment_response) if sentiment_response else {"error": "Sentiment analysis failed to return a response."}
        except (json.JSONDecodeError, TypeError):
            sentiment_data = {"error": "Failed to parse sentiment JSON.", "raw_response": sentiment_response}
        
        st.session_state.candidate_info['sentiment_analysis'] = sentiment_data
        st.session_state.candidate_info['score_feedback'] = score_data
        st.session_state.candidate_info['interview_timestamp'] = datetime.now().isoformat()
        
        try:
            if os.path.exists(CANDIDATE_DATA_FILE) and os.path.getsize(CANDIDATE_DATA_FILE) > 0:
                with open(CANDIDATE_DATA_FILE, "r") as f:
                    all_candidates_data = json.load(f)
            else:
                all_candidates_data = []
        except (json.JSONDecodeError, FileNotFoundError):
            all_candidates_data = []

        all_candidates_data.append(st.session_state.candidate_info)

        with open(CANDIDATE_DATA_FILE, "w") as f:
            json.dump(all_candidates_data, f, indent=4)
        
        st.toast("Candidate data saved successfully!")

    def _score_answers(self):
        """Scores the candidate's answers, parses the JSON, and saves the results."""
        questions = st.session_state.candidate_info.get('tech_questions_asked')
        answers = st.session_state.candidate_info.get('tech_question_answers')
        
        if not questions or not answers:
            return self._call_llm("Something went wrong and I can't find the questions or answers. Apologize and say a recruiter will be in touch.")

        prompt = templates.get_scoring_prompt(questions, answers)
        with st.spinner("Evaluating your answers..."):
            score_response = self._call_llm(prompt, model="llama3-70b-8192", temperature=0.1, json_only=True)
        
        st.session_state.conversation_stage = "end"

        if score_response:
            try:
                score_data = json.loads(score_response)
                self._save_results_to_json_file(score_data)
                final_message_instruction = "Inform the user that this concludes the screening, thank them for their responses, and let them know a recruiter will be in touch soon. Wish them a great day."
                return self._call_llm(final_message_instruction)
            except json.JSONDecodeError:
                self._save_results_to_json_file({"error": "Failed to parse score JSON.", "raw_response": score_response})
                return self._call_llm("Apologize that there was an issue with automated evaluation, but confirm their answers were saved for manual review. Thank them for their time.")
        else:
            self._save_results_to_json_file({"error": "Failed to generate score."})
            return self._call_llm("Apologize that you are having trouble evaluating the answers, but confirm they have been saved for manual review. Thank them for their time.")
