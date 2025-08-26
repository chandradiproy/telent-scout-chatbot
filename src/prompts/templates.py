# src/prompts/templates.py

def get_system_prompt():
    """
    Returns the system prompt that defines the chatbot's persona and instructions.
    """
    return """
    You are an intelligent, friendly, and professional Hiring Assistant for a recruitment agency called "TalentScout".
    Your purpose is to conduct an initial screening of candidates.
    You must gather specific information in a sequential and conversational manner.
    Do not deviate from this purpose.
    Maintain a polite and encouraging tone throughout the conversation.
    If a user's input is unclear or irrelevant, gently guide them back to the current question.
    Your responses should be concise and to the point.
    """

def get_tech_questions_prompt(tech_stack: str) -> str:
    """
    Generates a prompt to ask the LLM for technical questions based on a tech stack.

    Args:
        tech_stack: A string containing the candidate's declared technologies.

    Returns:
        A formatted prompt string.
    """
    return f"""
    Based on the following tech stack, please generate exactly 4 relevant and insightful technical questions.
    The questions should be suitable for an initial screening to gauge a candidate's proficiency.
    Do not number the questions. Each question should be separated by a newline.

    Tech Stack: "{tech_stack}"

    Generate the questions now.
    """
