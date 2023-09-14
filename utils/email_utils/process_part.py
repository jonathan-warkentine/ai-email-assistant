import base64

from utils import email_utils

def process_part(part, role):
    message_exchange = list()
    mime_types = ['text/plain', 'text/html']

    if part['mimeType'] in mime_types:
        data = part['body']['data']
        text = base64.urlsafe_b64decode(data).decode('utf-8')
        message_exchange.append({"role": role, "content": email_utils.strip_quoted_text(text)})
    elif part['mimeType'] == 'multipart/mixed':
        for subpart in part['parts']:
            message_exchange.extend(email_utils.process_part(subpart, role))

    return message_exchange