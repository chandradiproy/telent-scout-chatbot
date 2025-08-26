# 🤖 TalentScout AI Hiring Assistant

An intelligent, multilingual AI chatbot designed to conduct initial candidate screenings for the fictional recruitment agency, "TalentScout". This project leverages Large Language Models (LLMs) via the Groq API to create a dynamic, robust, and user-friendly hiring assistant that can converse in multiple languages.

---

## ✨ Features

This chatbot is equipped with a comprehensive set of features to streamline the initial hiring process:

* **Multilingual Support**: The chatbot begins by asking the candidate for their preferred language and conducts the entire interview in that language.
* **Conversational Information Gathering**: Sequentially collects key candidate details, including name, contact information (with email validation), years of experience, desired position, and tech stack.
* **Dynamic & Experience-Based Questioning**: Generates 4 unique technical questions tailored not only to the candidate's specific **tech stack** but also to their **years of experience**, ensuring relevant difficulty.
* **Intelligent Intent Detection**: Employs an LLM-based intent detection layer to handle situations where candidates try to evade questions, providing firm but polite guidance to keep the conversation on track.
* **Automated Answer Evaluation**: After the candidate provides answers, the system uses a powerful LLM (`llama3-70b-8192`) to:
    * Score each answer individually out of 10.
    * Provide a justification for each score.
    * Critically assess whether the answer is relevant to the question asked, penalizing irrelevant responses.
    * Calculate an overall score and provide a final summary.
* **Sentiment Analysis**: Performs an overall sentiment analysis of the entire conversation to gauge the candidate's disposition (Positive, Neutral, or Negative).
* **Persistent Data Storage**: All candidate information, Q&A, scoring, and sentiment analysis are saved and appended to a `candidate_data.json` file, creating a persistent record for recruiters.
* **Enhanced User Interface**: A clean and intuitive UI built with Streamlit, featuring:
    * Avatars for the user and assistant.
    * A "Start Over" button in the sidebar to easily reset the conversation.
    * A real-time, character-by-character streaming effect for a dynamic user experience.

---

## 📂 Project Structure

The project is organized into a modular and scalable structure to ensure maintainability and readability.

```
talent-scout-chatbot/
│
├── .gitignore
├── README.md
├── requirements.txt
├── .env
│
├── app.py                  # Main Streamlit application UI
├── candidate_data.json     # Output data file
│
└── src/
    ├── chatbot/
    │   └── core.py         # Core chatbot logic, state management, API calls
    │
    ├── prompts/
    │   └── templates.py    # Centralized prompt engineering templates
    │
    └── utils/
        └── helpers.py      # Utility functions (e.g., email validation)
```

---

## 🛠️ Tech Stack

* **Language**: Python 3.9+
* **Frontend**: Streamlit
* **LLM Provider**: Groq API (for high-speed inference)
* **Core Models**:
    * `llama3-8b-8192` for general conversation, intent detection, and question generation.
    * `llama3-70b-8192` for high-quality answer evaluation and scoring.
* **Libraries**: `python-dotenv`, `groq`, `streamlit`

---

## 🚀 Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/chandradiproy/telent-scout-chatbot.git](https://github.com/chandradiproy/telent-scout-chatbot.git)
cd telent-scout-chatbot
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

* **macOS / Linux**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
* **Windows**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

### 3. Install Dependencies

Install all the required Python libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

You will need an API key from [GroqCloud](https://console.groq.com/keys).

1.  Create a file named `.env` in the root of the project directory.
2.  Add your Groq API key to this file:
    ```
    GROQ_API_KEY="your_api_key_here"
    ```
The `.gitignore` file is already configured to prevent this file from being committed to Git.

---

## ▶️ Usage

Once the setup is complete, you can run the Streamlit application with a single command:

```bash
streamlit run app.py
```

This will open a new tab in your default web browser with the chatbot interface ready to go.

---

## 🧠 Prompt Engineering Strategy

The effectiveness of this chatbot relies on a multi-layered prompt engineering strategy:

1.  **Language-Aware System Prompt**: The master prompt now dynamically includes the candidate's chosen language, instructing the LLM to conduct the entire interaction in that language.
2.  **Experience-Based Question Generation**: The prompt for generating technical questions is populated with the candidate's tech stack and experience, instructing the LLM to tailor question difficulty and to return *only* a numbered list.
3.  **Intent Detection**: A specialized prompt is used to classify user input during the Q&A phase, allowing the system to robustly handle evasive or off-topic responses.
4.  **Strict JSON for Evaluation**: The scoring prompt instructs the LLM to act as a critical interviewer and return its evaluation in a strict JSON format. It includes a critical instruction to heavily penalize answers that are not relevant to the questions asked.

---

## 💡 Challenges and Solutions

* **Challenge**: The LLM would return conversational text along with JSON data, causing parsing errors.
    * **Solution**: The `_call_llm` function was enhanced with a robust regex to search for and extract the JSON block from the raw response, ignoring any surrounding text or markdown fences.
* **Challenge**: The chatbot would ask the wrong question at the wrong time (e.g., asking for an email after receiving the name).
    * **Solution**: The state management logic in `handle_response` was rewritten to be more explicit. It now processes the input for the *current* state before advancing to the *next* state, ensuring the conversation flows correctly.
* **Challenge**: The multilingual feature initially failed, with the chatbot reverting to English for simple conversational turns.
    * **Solution**: The hardcoded English responses in the `conversation_stages` list were replaced with dynamic instructions. The chatbot now uses the LLM to generate *every* response, ensuring it always adheres to the user's selected language.

---
