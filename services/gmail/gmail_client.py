from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient import discovery, errors
from app_data.data_util import Data_store
from utils.deduplicate_list import deduplicate_list 
from utils.email_utils import extract_email_address_from_text, convert_line_breaks_to_html, strip_quoted_text, extract_last_message_in_thread, extract_message_header_value

import base64

class Gmail_client:
    """
    Provides a set of functions to interact with the Gmail API.
    """

    def __init__(self, config):
        """
        Initializes the Gmail API client with the provided credentials.

        :param config: curried config parse function containing all needed configs
        """
        self.user = config('user')
        self.data_store = Data_store(config('data_store_filepath'))
        self.credentials = service_account.Credentials.from_service_account_info(config('credentials', return_dicts=True), scopes=config('client_scopes'))
        self.delegated_credentials = self.credentials.with_subject(self.user)
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

    def filter_threads_awaiting_response(self, threads):
        """
        Filters Gmail threads that have not yet been replied to.

        :param threads: List of Gmail threads.
        :return: Filtered list of Gmail threads that need a response.
        """
        threads_awaiting_response = list()

        for thread in threads:
            last_message = extract_last_message_in_thread(thread)
            
            sender_email = extract_email_address_from_text(
                extract_message_header_value(
                    message=last_message,
                    header_name='From'
                )
            )

            # Check if the sender is not the authenticated user
            if sender_email != self.user:
                threads_awaiting_response.append(thread)

        return threads_awaiting_response

    def save_email_draft(self, email):
        try:
            wrapped_email = {
            'message': email
            }
            self.client.users().drafts().create(userId="me", body=wrapped_email).execute()

        except errors.HttpError as e:
            print(F'An error occurred saving email draft: {e}')

    def fetch_new_message_thread_ids(self):
        new_message_thread_ids = list()
        new_histories = self.fetch_new_histories()
        if (new_histories != None):
            new_messages = self._parse_new_messages_from_histories(new_histories)
            new_message_thread_ids = self._parse_message_thread_ids_from_messages(new_messages)

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

    def _parse_thread_for_messages(self, thread):
        return thread.get('messages')

    def _process_part(self, part, role):
        message_exchange = list()
        mime_types = ['text/plain', 'text/html']

        if part['mimeType'] in mime_types:
            data = part['body']['data']
            text = base64.urlsafe_b64decode(data).decode('utf-8')
            message_exchange.append({"role": role, "content": strip_quoted_text(text)})
        elif part['mimeType'] == 'multipart/mixed':
            for subpart in part['parts']:
                message_exchange.extend(self._process_part(subpart, role))

        return message_exchange

    def _parse_new_messages_from_histories(self, histories):
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
    
    def _parse_message_thread_ids_from_messages(self, messages):
        message_thread_ids = list()
        for message in messages:
            message_thread_ids.append(message.get('threadId'))
        
        return deduplicate_list(message_thread_ids)

    # TODO: convert to multipart mime type if including attachments
    def _compose_email(self, recipient, subject, message_text, thread_id, in_reply_to):
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

    # CURRENTLY NOT IN USE
    # def _send_email(self, email):
    #     try:
    #         request = self.client.users().messages().send(userId=self.user, body = email)
    #         response = request.execute()

    #         return response
        
    #     except errors.HttpError as e:
    #         print(f"An error occurred sending email: {e}")
