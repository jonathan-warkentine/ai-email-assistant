from google.oauth2 import service_account
from googleapiclient import discovery, errors
from app_data.data_util import Data_store
from utils import email_utils

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
            new_messages = email_utils.parse_new_messages_from_histories(new_histories)
            new_message_thread_ids = email_utils.parse_message_thread_ids_from_messages(new_messages)

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

    # CURRENTLY NOT IN USE
    # def send_email(self, email):
    #     try:
    #         request = self.client.users().messages().send(userId=self.user, body = email)
    #         response = request.execute()

    #         return response
        
    #     except errors.HttpError as e:
    #         print(f"An error occurred sending email: {e}")
