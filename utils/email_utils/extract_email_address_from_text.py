import re

def extract_email_address_from_text(text):
    # Regular expression for matching an email
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if match:
        return match.group(0)  # if match, return the email
    else:
        return None  # if no match, return None