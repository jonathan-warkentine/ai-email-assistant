from google.auth.transport.requests import Request

from gmail import GmailAPI

######################################################################################
#                          Initialize our Gmail Client                               #
######################################################################################
gmail_client = GmailAPI(
    credentials_file_path='service_account_key.json', 
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

print(gmail_client.delegated_credentials.token)


######################################################################################
#                                       LOGIC                                        #
######################################################################################

# Sync new messages, for each new message:
    # existing client?