from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient import discovery, errors
from src.utils.data_util import Data_store
from src.utils.dedeplicate_list import deduplicate_list

import base64
import re

class GmailAPI:
    def __init__(self, credentials_file_path, scopes=['https://mail.google.com/'], user='me', data_store_filepath='./gmail.json'):
        self.user = user
        self.data_store = Data_store('src/gmail/gmail.json')
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file_path, scopes=scopes
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
            headers = last_message['payload']['headers']
            from_header = next(header for header in headers if header['name'] == 'From')
            sender = from_header['value']
            sender_email = self.extract_email(sender)

            if sender_email != self.user:
                threads_needing_response.append(thread)

        return threads_needing_response

    def extract_last_message_in_thread(self, thread):
        return thread['messages'][-1]


    def extract_email(self, text):
        email = None
        match = re.search(r'<(.*)>', text)
        if match:
            email = match.group(1)
        return email

    def parse_thread_for_messages(self, thread):
        message_exchange = []
        thread_messages = thread.get('messages')

        for message in thread_messages:
            try:
                headers = message['payload']['headers']
                sender_email = next(header['value'] for header in headers if header['name'] == 'From')

                role = "assistant" if self.user in sender_email else "user"

                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body']['data']
                            text = base64.urlsafe_b64decode(data).decode('utf-8')
                            message_exchange.append({"role": role, "content": self._strip_quoted_text(text)})
                else:
                    data = message['payload']['body']['data']
                    text = base64.urlsafe_b64decode(data).decode('utf-8')
                    message_exchange.append({"role": role, "content": self._strip_quoted_text(text)})
            except KeyError:
                continue
        return message_exchange

    def _strip_quoted_text(self, text):
        lines = text.split('\n')
        stripped_lines = []
        for line in lines:
            line_stripped = line.strip() # Remove leading/trailing whitespaces
            if line_stripped.startswith('>'):
                continue
            # Remove 'On ... wrote: ... \n' using regex, anywhere in the line
            line_stripped = re.sub(r'On .+ wrote:.+\n', '', line_stripped, flags=re.IGNORECASE).strip()
            if line_stripped:  # Exclude empty lines
                stripped_lines.append(line_stripped)
        return '\n'.join(stripped_lines)

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
        messages = []
        for history in histories:
            messages_added = history.get('messagesAdded')
            if (messages_added == None):
                continue
            
            for message in messages_added:
                messages.append(message.get('message'))
        
        return messages
    
    def parse_message_thread_ids_from_messages(self, messages):
        message_thread_ids = []
        for message in messages:
            message_thread_ids.append(message.get('threadId'))
        
        return deduplicate_list(message_thread_ids)

    def compose_email(self, recipient, subject, message_text, thread_id):
        email = MIMEText(message_text)
        email['to'] = recipient
        email['from'] = self.user
        email['subject'] = subject
            
        raw_email = base64.urlsafe_b64encode(email.as_bytes()).decode("utf-8")
        email_body = {'raw': raw_email, 'threadId': thread_id}
        return email_body
    
    # TODO: make sure it attaches to existing threads if any
    def send_email(self, email):
        try:
            request = self.client.users().messages().send(userId=self.user, body = email)
            response = request.execute()

            return response.get
        
        except errors.HttpError as e:
            print(f"An error occurred: {e}")

    def extract_subject_of_last_message_in_thread(self, thread):
        last_message = self.extract_last_message_in_thread(thread)
        headers = last_message['payload']['headers']
        for header in headers:
            if header['name'] == 'Subject':
                return header['value']
            
    # TODO: consolidate all logic after finding last email in thread in a higher level function above
    def extract_email_address_of_sender_of_last_message_in_thread(self, thread):
        last_message = self.extract_last_message_in_thread(thread)
        headers = last_message['payload']['headers']
        for header in headers:
            if header['name'] == 'From':
                extracted_email = self.extract_email(header['value'])
                return extracted_email