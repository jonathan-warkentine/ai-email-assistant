from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from googleapiclient import discovery, errors
from src.utils.data_util import Data_store

import os
import json

class GmailAPI:
    def __init__(self, credentials_file_path, scopes=['https://mail.google.com/'], user='me', data_store_filepath='./gmail.json'):
        self.user = user
        self.data_store = Data_store('src/gmail/gmail.json')
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file_path, scopes=scopes
        )
        self.delegated_credentials = self.credentials.with_subject(user)
        self.client = discovery.build('gmail', 'v1', credentials=self.delegated_credentials)

    def get_new_message_ids(self):
        new_histories = self.fetch_new_histories()
        if (new_histories == None):
            return None
        
        new_messages = self.parse_new_messages_from_histories(new_histories)
        new_message_ids = self.parse_message_ids_from_messages(new_messages)

        return new_message_ids

    def fetch_new_histories(self):
        try:
            request = self.client.users().history().list(userId=self.user, startHistoryId=self.data_store.read('historyId'))
            response = request.execute()

            # # Update historyId for future syncing
            # self.data_store.write('historyId', response.get('historyId))

            return response.get('history')
        
        except errors.HttpError as e:  # Catch all exceptions
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
    
    def parse_message_ids_from_messages(self, messages):
        message_ids = []
        for message in messages:
            message_ids.append(message.get('id'))
        
        return message_ids
