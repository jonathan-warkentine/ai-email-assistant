from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient import discovery, errors
from app_data.data_util import Data_store
from utils.deduplicate_list import deduplicate_list 
from utils.email_utils.extract_email_from_text import extract_email_from_text
from utils.email_utils.convert_line_breaks_to_html import convert_line_breaks_to_html
from utils.email_utils.strip_quoted_text import strip_quoted_text

import base64

class Gmail_client:
    """
    Provides a set of functions to interact with the Gmail API.
    """

    def __init__(self, credentials_filepath, scopes=['https://mail.google.com/'], user='me', data_store_filepath='./gmail.json'):
        """
        Initializes the Gmail API client with the provided credentials.

        :param credentials_filepath: Path to the credentials file for Gmail API access.
        :param scopes: List of Gmail API scopes.
        :param user: Email address of the user, default is 'me' which is the authenticated user.
        :param data_store_filepath: Path to the file for storing data.
        """
        self.user = user
        self.data_store = Data_store(data_store_filepath)
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_filepath, scopes=scopes
        )
        self.delegated_credentials = self.credentials.with_subject(user)
        self.client = discovery.build('gmail', 'v1', credentials=self.delegated_credentials)

    def synchronize_gmail_client(self):
        """
        Uses historyId of latest message to update historyId in data store.
        """
        try:
            # First get the latest historyId
            message_list = self.client.users().messages().list(userId="me").execute().get('messages')
            latest_message_id = message_list[0].get("id")
            latest_message = self.client.users().messages().get(userId="me", id=latest_message_id).execute()
            latest_history_id = latest_message.get("historyId")
            self.data_store.write("historyId", latest_history_id)

            return latest_history_id
        
        except errors.HttpError as e:
            print(f"An error occurred synchronizing the Gmail client: {e}")

    def fetch_threads_with_new_messages(self):
        """
        Fetches Gmail threads that contain new messages.

        :return: List of Gmail threads with new messages.
        """
        threads = list()
        new_messages_thread_ids = self.fetch_new_message_thread_ids()
        
        if new_messages_thread_ids:
            for thread_id in new_messages_thread_ids:
                threads.append(self.fetch_thread(thread_id))
        
        return threads

    def fetch_thread(self, thread_id):
        """
        Fetches a specific Gmail thread by its ID.

        :param thread_id: The ID of the Gmail thread.
        :return: Gmail thread.
        """
        try:
            request = self.client.users().threads().get(
                userId=self.user, 
                id=thread_id,
                format='full'
            )
            return request.execute()
        
        except errors.HttpError as e:
            print(f"An error occurred fetching threads from Gmail: {e}")

    def filter_threads_needing_response(self, threads):
        """
        Filters Gmail threads that need a response from the authenticated user.

        :param threads: List of Gmail threads.
        :return: Filtered list of Gmail threads that need a response.
        """
        threads_needing_response = list()

        for thread in threads:
            last_message = self.extract_last_message_in_thread(thread)
            
            sender_email = extract_email_from_text(
                self.extract_message_header_value(
                    message=last_message,
                    header_name='From'
                )
            )

            # Check if the sender is not the authenticated user
            if sender_email != self.user:
                threads_needing_response.append(thread)

        return threads_needing_response

    def extract_last_message_in_thread(self, thread):
        return thread['messages'][-1]

    def parse_thread_for_messages(self, thread):
        return thread.get('messages')

    def process_part(self, part, role):
        message_exchange = list()
        mime_types = ['text/plain', 'text/html']

        if part['mimeType'] in mime_types:
            data = part['body']['data']
            text = base64.urlsafe_b64decode(data).decode('utf-8')
            message_exchange.append({"role": role, "content": strip_quoted_text(text)})
        elif part['mimeType'] == 'multipart/mixed':
            for subpart in part['parts']:
                message_exchange.extend(self.process_part(subpart, role))

        return message_exchange

    def prepare_messages_for_chatgpt(self, messages):
        """
        Process a list of email messages fetched from the Gmail API and prepares them 
        in a format suitable for chat. It distinguishes between the 'user' and the 
        'assistant' based on the email sender.
        """
        message_exchange = list()

        for message in messages:
            try:
                sender_email = extract_email_from_text(
                    self.extract_message_header_value(
                        message=message,
                        header_name='From'
                    )
                )

                role = 'assistant' if sender_email == self.user else 'user'
                
                parts = message['payload'].get('parts', [])
                
                # First try to find a text/plain part
                text_parts = [part for part in parts if is_text_part(part)]

                if text_parts:
                    # Use only the first text/plain part found
                    message_exchange.extend(self.process_part(text_parts[0], role))
                elif parts:  # If no text/plain part was found, process all other parts
                    for part in parts:
                        message_exchange.extend(self.process_part(part, role))
                else:
                    # If there are no parts, decode the message directly
                    data = message['payload']['body']['data']
                    text = base64.urlsafe_b64decode(data).decode('utf-8')
                    message_exchange.append({"role": role, "content": strip_quoted_text(text)})

            except KeyError:
                continue

        return message_exchange

            
    def fetch_new_message_thread_ids(self):
        new_message_thread_ids = list()
        new_histories = self.fetch_new_histories()
        if (new_histories != None):
            new_messages = self.parse_new_messages_from_histories(new_histories)
            new_message_thread_ids = self.parse_message_thread_ids_from_messages(new_messages)

        return new_message_thread_ids

    def fetch_new_histories(self):
        try:
            request = self.client.users().history().list(userId=self.user, startHistoryId=self.data_store.read('historyId'))
            response = request.execute()

            # Update historyId for future syncing
            self.data_store.write('historyId', response.get('historyId'))

            return response.get('history')
        
        except errors.HttpError as e:
            print(f"An error occurred fetching new Gmail histories: {e}")
            print(f"Reverting to a full synchronization of the Gmail client; any new messages will be disregarded.")
            self.synchronize_gmail_client()
            return self.fetch_new_histories()

    def parse_new_messages_from_histories(self, histories):
        """
        Extracts new messages from the provided Gmail histories.

        :param histories: List of Gmail history objects.
        :return: List of new Gmail messages.
        """
        messages = list()
        for history in histories:
            messages_added = history.get('messagesAdded')
            
            # Check if there are any messages added in the current history
            if messages_added:
                for message in messages_added:
                    messages.append(message.get('message'))
        
        return messages
    
    def parse_message_thread_ids_from_messages(self, messages):
        message_thread_ids = list()
        for message in messages:
            message_thread_ids.append(message.get('threadId'))
        
        return deduplicate_list(message_thread_ids)

    # TODO: convert to multipart mime type if including attachments
    def compose_email(self, recipient, subject, message_text, thread_id, in_reply_to):
        """
        Composes an email.

        :param recipient: Email recipient.
        :param subject: Email subject.
        :param message_text: Content of the email.
        :param thread_id: ID of the Gmail thread.
        :param in_reply_to: Message-ID this email is in reply to.
        :return: Email object ready to be sent or saved as draft.
        """
        message_text = convert_line_breaks_to_html(message_text)

        # Prepare the MIME message with appropriate headers
        mime_message = MIMEText(message_text, 'html')
        mime_message['To'] = recipient
        mime_message['From'] = self.user
        mime_message['Subject'] = subject
        mime_message['In-Reply-To'] = in_reply_to
        mime_message['References'] = in_reply_to

        raw_email = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        email_body = {
            'raw': raw_email, 
            'threadId': thread_id
        }

        return email_body

    def save_email_draft(self, email):
        try:
            wrapped_email = {
            'message': email
            }
            self.client.users().drafts().create(userId="me", body=wrapped_email).execute()

        except errors.HttpError as e:
            print(F'An error occurred saving email draft: {e}')


    def send_email(self, email):
        try:
            request = self.client.users().messages().send(userId=self.user, body = email)
            response = request.execute()

            return response
        
        except errors.HttpError as e:
            print(f"An error occurred sending email: {e}")

    def extract_message_header_value(self, message, header_name):
        """
        Extracts the value of a specific header from a Gmail message.

        :param message: Gmail message object.
        :param header_name: Name of the header to extract.
        :return: Value of the specified header or None if not found.
        """
        headers = message['payload']['headers']
        for header in headers:
            if header['name'] == header_name:
                return header['value']

def is_text_part(part):
    # Return True if the part is plain text, False otherwise
    return part.get("mimeType") == "text/plain"