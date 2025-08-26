# 🤖 TalentScout AI Hiring Assistant

An intelligent, conversational AI chatbot designed to conduct initial candidate screenings for the fictional recruitment agency, "TalentScout". This project leverages Large Language Models (LLMs) via the Groq API to create a dynamic, robust, and user-friendly hiring assistant.


---

## ✨ Features

This chatbot is equipped with a comprehensive set of features to streamline the initial hiring process:

* **Conversational Information Gathering**: Sequentially collects key candidate details:
    * Full Name
    * Email & Phone Number (with validation)
    * Years of Experience
    * Desired Position & Current Location
    * Primary Tech Stack
* **Dynamic Technical Questioning**: Generates 4 unique technical questions tailored not only to the candidate's specific **tech stack** but also to their **years of experience**, ensuring relevant difficulty.
* **Intelligent Intent Detection**: Employs an LLM-based intent detection layer to handle situations where candidates try to evade questions, providing firm but polite guidance to keep the conversation on track.
* **Automated Answer Evaluation**: After the candidate provides answers, the system uses a powerful LLM (`llama3-70b-8192`) to:
    * Score each answer individually out of 10.
    * Provide a justification for each score.
    * Critically assess whether the answer is relevant to the question asked.
    * Calculate an overall score and provide a final summary.
* **Sentiment Analysis**: Performs an overall sentiment analysis of the entire conversation to gauge the candidate's disposition (Positive, Neutral, Negative).
* **Persistent Data Storage**: All candidate information, Q&A, scoring, and sentiment analysis are saved and appended to a `candidate_data.json` file, creating a persistent record for recruiters.
* **Enhanced User Interface**: A clean and intuitive UI built with Streamlit, featuring:
    * Avatars for the user and assistant.
    * A "Start Over" button to easily reset the conversation.
    * Real-time "thinking" indicators and a simulated typing effect for a better user experience.

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

1.  **System Prompt**: A master prompt defines the chatbot's persona, its objective, and its professional boundaries, ensuring it stays on task.
2.  **Experience-Based Question Generation**: The prompt for generating technical questions is dynamically populated with the candidate's tech stack and years of experience, instructing the LLM to tailor the question difficulty accordingly. We also explicitly instruct it to return *only* a numbered list to avoid conversational filler.
3.  **Intent Detection**: A specialized prompt is used to classify user input during the Q&A phase. This allows the system to differentiate between a genuine answer and an attempt to evade the question, making the chatbot much more robust.
4.  **Structured JSON for Evaluation**: The scoring prompt instructs the LLM to act as a critical interviewer and return its evaluation in a strict JSON format. This allows for reliable, programmatic parsing of the results and includes a specific instruction to heavily penalize answers that are not relevant to the questions asked.

---

## 💡 Challenges and Solutions

* **Challenge**: The LLM would occasionally return conversational text along with the structured JSON data, causing parsing errors.
    * **Solution**: The `_call_llm` function was enhanced with a robust regex to search for and extract the JSON block from the raw response, ignoring any surrounding text or markdown fences.
* **Challenge**: Candidates could provide answers that were technically correct but completely irrelevant to the questions asked, yet still receive a high score.
    * **Solution**: The scoring prompt was updated with a **critical instruction** to first validate the relevance of an answer to its question and to assign a very low score if they did not match.
* **Challenge**: The chatbot followed a rigid conversation flow and was easily derailed by unexpected user inputs (e.g., asking to regenerate questions).
    * **Solution**: An intent detection layer was implemented. This allows the chatbot to understand the user's intent before acting, enabling it to gracefully handle evasive or off-topic responses.

---
