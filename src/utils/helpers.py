# src/utils/helpers.py

import re

def is_valid_email(email: str) -> bool:
    """
    Validates if the provided string is a valid email address.

    Args:
        email: The email string to validate.

    Returns:
        True if the email is valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None
    