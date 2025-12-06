import re
from datetime import datetime

def validate_roll_no(roll_no):
    """Validate roll number format"""
    if not roll_no or len(roll_no) < 3:
        return False, "Roll number must be at least 3 characters long."
    
    if not re.match(r'^[A-Z0-9]+$', roll_no.upper()):
        return False, "Roll number can only contain letters and numbers."
    
    return True, ""

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    
    return True, ""

def validate_marks(marks, max_marks):
    """Validate marks"""
    if marks < 0:
        return False, "Marks cannot be negative."
    
    if marks > max_marks:
        return False, f"Marks cannot exceed maximum marks ({max_marks})."
    
    return True, ""

def validate_date(date_str):
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD."

def validate_contact(contact):
    """Validate contact number"""
    if not contact:
        return True, ""  # Contact is optional
    
    # Remove spaces and dashes
    contact = contact.replace(" ", "").replace("-", "")
    
    if not contact.isdigit():
        return False, "Contact number must contain only digits."
    
    if len(contact) < 10:
        return False, "Contact number must be at least 10 digits."
    
    return True, ""

def validate_username(username):
    """Validate username"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long."
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores."
    
    return True, ""