from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient import discovery, errors
from utils.data_util import Data_store
from utils.deduplicate_list import deduplicate_list 
from utils.extract_email_from_text import extract_email_from_text
from utils.convert_line_breaks_to_html import convert_line_breaks_to_html
from utils.strip_quoted_text import strip_quoted_text

import base64

class GmailAPI:
    def __init__(self, credentials_file_path, scopes = ['https://mail.google.com/'], user = 'me', data_store_filepath = './gmail.json'):
        self.user = user
        self.data_store = Data_store('gmail_api/gmail.json')
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file_path, scopes = scopes
        )
        self.delegated_credentials = self.credentials.with_subject(user)
        self.client = discovery.build('gmail', 'v1', credentials=self.delegated_credentials)

    def fetch_threads_with_new_messages(self):
        threads = list()
        new_messages_thread_ids = self.fetch_new_message_thread_ids()
        
        if (new_messages_thread_ids != None):
            for thread_id in new_messages_thread_ids:
                threads.append(self.fetch_thread(thread_id))
        
        return threads

    def fetch_thread(self, thread_id):
        try:
            request = self.client.users().threads().get(
                userId = self.user, 
                id = thread_id,
                format = 'full'
            )
            return request.execute()
        
        except errors.HttpError as e:
            print(f"An error occurred: {e}")

    def filter_threads_needing_response(self, threads):
        threads_needing_response = list()

        for thread in threads:
            last_message = self.extract_last_message_in_thread(thread)
            
            sender_email = extract_email_from_text(
                self.extract_message_header_value(
                    message = last_message,
                    header_name = 'From'
                )
            )

            if (sender_email != self.user):
                threads_needing_response.append(thread)

        return threads_needing_response

    def extract_last_message_in_thread(self, thread):
        return thread['messages'][-1]

    def parse_thread_for_messages(self, thread):
        message_exchange = list()
        thread_messages = thread.get('messages')

        for message in thread_messages:
            try:
                sender_email = extract_email_from_text(
                    self.extract_message_header_value(
                        message = message,
                        header_name = 'From'
                    )
                )

                role = 'assistant' 
                if sender_email == self.user:
                    role = 'user'

                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body']['data']
                            text = base64.urlsafe_b64decode(data).decode('utf-8')
                            message_exchange.append({"role": role, "content": strip_quoted_text(text)})
                else:
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
            print(f"An error occurred: {e}")

    def parse_new_messages_from_histories(self, histories):
        messages = list()
        for history in histories:
            messages_added = history.get('messagesAdded')
            if (messages_added == None):
                continue
            
            for message in messages_added:
                messages.append(message.get('message'))
        
        return messages
    
    def parse_message_thread_ids_from_messages(self, messages):
        message_thread_ids = list()
        for message in messages:
            message_thread_ids.append(message.get('threadId'))
        
        return deduplicate_list(message_thread_ids)

    def compose_email(self, recipient, subject, message_text, thread_id, in_reply_to):
        message_text = convert_line_breaks_to_html(message_text)

        mime_message = MIMEMultipart()
        mime_message['To'] = recipient
        mime_message['From'] = self.user
        mime_message['Subject'] = subject
        mime_message['In-Reply-To'] = in_reply_to
        mime_message['References'] = in_reply_to
        mime_message.attach(MIMEText(message_text, 'html'))    
        
        raw_email = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        email_body = {
            'raw': raw_email, 
            'threadId': thread_id
        }
        
        return email_body
    
    # TODO: make sure it attaches to existing threads if any
    def send_email(self, email):
        try:
            request = self.client.users().messages().send(userId=self.user, body = email)
            response = request.execute()

            return response
        
        except errors.HttpError as e:
            print(f"An error occurred: {e}")
            
    def extract_message_header_value(self, message, header_name):
        headers = message['payload']['headers']
        for header in headers:
            # print(f'{header["name"]} : {header["value"]}')
            if header['name'] == header_name:
                return header['value']
