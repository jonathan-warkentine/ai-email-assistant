from google.auth.transport.requests import Request

from src.gmail.gmail_api import GmailAPI

######################################################################################
#                          Initialize our Gmail Client                               #
######################################################################################
gmail_client = GmailAPI(
    credentials_file_path='src/gmail/service_account_key.json', 
    scopes=['https://mail.google.com/'], 
    user='automation@topdawgjunkremoval.com', 
    data_store_filepath='./data.json'
)

######################################################################################
#                          TODO: Initialize our OpenAI Client                        #
######################################################################################

######################################################################################
#                          TODO: Initialize our Workiz Client                        #
######################################################################################



######################################################################################
#                    (obtain & print token for debugging purposes)                   #
######################################################################################
gmail_client.delegated_credentials.refresh(Request())

print(gmail_client.delegated_credentials.token + '\n')


######################################################################################
#                                       LOGIC                                        #
######################################################################################

print(gmail_client.get_new_message_ids())

# Sync new messages, for each new message:
    # existing client?