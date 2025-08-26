# src/prompts/templates.py

def get_system_prompt():
    """
    Returns the system prompt that defines the chatbot's persona and instructions.
    """
    return """
    You are an intelligent, friendly, and professional Hiring Assistant for a recruitment agency called "TalentScout".
    Your purpose is to conduct an initial screening of candidates by gathering specific information and asking technical questions.
    You must follow the instructions given to you and not deviate from your purpose.
    Maintain a polite and encouraging tone, but be firm when a user tries to bypass a question.
    Your responses should be concise and to the point.
    """

def get_intent_detection_prompt(user_input: str, current_stage: str) -> str:
    """
    Generates a prompt to classify the user's intent.
    """
    return f"""
    A user is interacting with a hiring chatbot. The chatbot is currently in the '{current_stage}' stage of the conversation, having just asked a set of technical questions.
    The user's latest input is: "{user_input}"

    Analyze the user's input and classify its intent into one of the following categories:
    1.  ANSWERING_QUESTION: The user is directly answering the technical questions or providing the requested information.
    2.  EVADING_QUESTION: The user is trying to bypass the question, asking for different questions, complaining about the questions, or asking the chatbot to do something else.
    3.  IRRELEVANT: The user's input is off-topic, a greeting, or unrelated to the hiring process.

    Respond with only the category name (e.g., "ANSWERING_QUESTION").
    """

def get_tech_questions_prompt(tech_stack: str, experience: str) -> str:
    """
    Generates a prompt to ask the LLM for technical questions based on a tech stack and experience level.
    """
    return f"""
    Your task is to act as a senior technical recruiter. Generate exactly 4 technical questions based *specifically* on the technologies listed in the tech stack below.

    Crucially, you must tailor the difficulty and depth of the questions to the candidate's stated years of experience.
    - For junior roles (0-2 years), focus on fundamental concepts and syntax.
    - For mid-level roles (3-5 years), focus on practical application, best practices, and common patterns.
    - For senior roles (5+ years), focus on architecture, scalability, and trade-offs.

    Return ONLY the questions as a numbered list (1., 2., 3., 4.) and nothing else. Do not add any introductory or concluding text.

    Tech Stack: "{tech_stack}"
    Years of Experience: "{experience}"

    Generate the 4 questions now.
    """

def get_scoring_prompt(questions: str, answers: str) -> str:
    """
    Generates a prompt to score the candidate's answers and return a JSON object.
    """
    return f"""
    You are an expert technical interviewer. Your task is to evaluate a candidate's answers to a set of technical questions and provide a structured JSON response.

    Here are the numbered questions that were asked:
    ---
    {questions}
    ---

    Here are the candidate's answers. Note that the candidate may not have followed the numbering format, so you must intelligently map their answers to the corresponding questions.
    ---
    {answers}
    ---

    Please perform the following and return ONLY a single valid JSON object with no other text or explanations:
    1.  Create a key "evaluation" which is a list of objects. Each object should represent one question and have three keys: "question_number" (int), "score" (int out of 10), and "justification" (a brief, one-sentence reason for the score).
    2.  Create a key "overall_score" (float, average of the individual scores).
    3.  Create a key "summary" (string, a 2-3 sentence overview of the candidate's technical proficiency).

    Example of the required JSON format:
    {{
      "evaluation": [
        {{
          "question_number": 1,
          "score": 8,
          "justification": "The candidate provided a solid and accurate explanation."
        }}
      ],
      "overall_score": 8.0,
      "summary": "The candidate demonstrates a good understanding of the core concepts."
    }}
    """

def get_sentiment_analysis_prompt(conversation_history: str) -> str:
    """
    Generates a prompt to analyze the sentiment of the conversation.
    """
    return f"""
    Analyze the sentiment of the following conversation between a hiring assistant and a candidate.
    Classify the overall sentiment as "Positive", "Neutral", or "Negative".
    Provide a brief, one-sentence justification for your classification.
    Return ONLY a single valid JSON object with two keys: "sentiment" and "justification".

    Conversation History:
    ---
    {conversation_history}
    ---

    Example of the required JSON format:
    {{
      "sentiment": "Positive",
      "justification": "The candidate was polite, cooperative, and provided detailed answers."
    }}
    """
