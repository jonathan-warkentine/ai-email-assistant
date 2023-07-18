from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build

import os
import json

class GmailAPI:
    def __init__(self, credentials_file_path, scopes=['https://mail.google.com/'], user='me', data_store_filepath='./data.json'):
        self.user = user
        with open('data.json', 'r') as f:
            self.data = json.load(f)
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file_path, scopes=scopes
        )
        self.delegated_credentials = self.credentials.with_subject(user)
        self.client = build('gmail', 'v1', credentials=self.delegated_credentials)

    # Returns 
    def get_new_message_ids(self):
        request = self.service.users().history().list(userId=self.user, startHistoryId=self.data.historyId)
        response = request.execute()
        return response 
    
    # Returns new messages since last sync
    def get_new_messages(self):
        request = self.service.users().history().list(userId=self.user)