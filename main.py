from google.auth.transport.requests import Request

from src.gmail.gmail_api import GmailAPI
from src.openai.chatgpt_api import ChatGPT_API
from src.job import Job

######################################################################################
#                          Initialize our Gmail Client                               #
######################################################################################
gmail_api = GmailAPI(
    credentials_file_path='src/gmail/service_account_key.json', 
    scopes=['https://mail.google.com/'], 
    user='automation@topdawgjunkremoval.com', 
    data_store_filepath='./data.json'
)

######################################################################################
#                          TODO: Initialize our OpenAI Client                        #
######################################################################################
chatgpt_api = ChatGPT_API()

######################################################################################
#                          TODO: Initialize our Workiz Client                        #
######################################################################################



######################################################################################
#                    (obtain & print token for debugging purposes)                   #
#                                   TODO: DELETE!!                                   #
######################################################################################
# gmail_api.delegated_credentials.refresh(Request())

# print(gmail_api.delegated_credentials.token + '\n')


######################################################################################
#                                       LOGIC                                        #
######################################################################################

# DEBUGGING:
threads_with_new_messages = gmail_api.fetch_threads_with_new_messages()
threads_needing_response = gmail_api.filter_threads_needing_response(threads_with_new_messages)

# Prepare thread as conversation for ChatGPT API call ('messages' parameter)
jobs = list()
for thread in threads_needing_response:
    conversation = gmail_api.parse_thread_for_messages(thread)
    subject_of_last_email = gmail_api.extract_subject_of_last_message_in_thread(thread)
    email_address_of_sender = gmail_api.extract_email_address_of_sender_of_last_message_in_thread(thread)
    job = Job(recipient = email_address_of_sender, subject = subject_of_last_email, conversation = conversation, thread = thread)
    jobs.append(job)

if jobs: 
    for job in jobs:
        chatgpt_response = chatgpt_api.fetch_chatgpt_response(messages = job.conversation)
        message_text = chatgpt_response.get('choices')[0].get('message').get('content')
        email_draft = gmail_api.compose_email(recipient = job.recipient, subject = job.subject, message_text = message_text, thread_id = thread.get('id'))
        print(email_draft)