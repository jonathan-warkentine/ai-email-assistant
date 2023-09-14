import base64
from email.mime.text import MIMEText

from utils import email_utils

# TODO: convert to multipart mime type if including attachments
def compose_email(user, recipient, subject, message_text, thread_id, in_reply_to):
    """
    Composes an email.

    :param recipient: Email recipient.
    :param subject: Email subject.
    :param message_text: Content of the email.
    :param thread_id: ID of the Gmail thread.
    :param in_reply_to: Message-ID this email is in reply to.
    :return: Email object ready to be sent or saved as draft.
    """
    message_text = email_utils.convert_line_breaks_to_html(message_text)

    # Prepare the MIME message with appropriate headers
    mime_message = MIMEText(message_text, 'html')
    mime_message['To'] = recipient
    mime_message['From'] = user
    mime_message['Subject'] = subject
    mime_message['In-Reply-To'] = in_reply_to
    mime_message['References'] = in_reply_to

    raw_email = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
    email_body = {
        'raw': raw_email, 
        'threadId': thread_id
    }

    return email_body