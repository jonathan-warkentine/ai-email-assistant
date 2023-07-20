from google.auth.transport.requests import Request

from src.gmail.gmail_api import GmailAPI
from src.openai.chatgpt_api import ChatGPT_API
from src.job import Job
from src.utils.extract_email_from_text import extract_email_from_text

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
    last_email_in_thread = gmail_api.extract_last_message_in_thread(thread)
    message_id_of_last_email = gmail_api.extract_message_header_value(
        message = last_email_in_thread,
        header_name = 'Message-Id'
    )
    subject_of_last_email = gmail_api.extract_message_header_value(
        message = last_email_in_thread,
        header_name = 'Subject'
    )
    email_address_of_sender_of_last_email = extract_email_from_text(
        gmail_api.extract_message_header_value(
            message = last_email_in_thread,
            header_name = 'From'
        )
    )
    job = Job(
        recipient = email_address_of_sender_of_last_email, 
        subject = subject_of_last_email, 
        conversation = conversation, 
        thread = thread,
        in_reply_to = message_id_of_last_email
    )
    jobs.append(job)
    ################################################
    #####      PRINT FOR DEBUGGING PURPOSES    #####
    ################################################
    # print(f'\n"{subject_of_last_email}" from {email_address_of_sender_of_last_email} (message_id = {message_id_of_last_email})')
    ################################################

for job in jobs:
    chatgpt_response = chatgpt_api.fetch_chatgpt_response(messages = job.conversation)
    message_text = chatgpt_response.get('choices')[0].get('message').get('content')
    email_draft = gmail_api.compose_email(
        recipient = job.recipient, 
        subject = job.subject, 
        message_text = message_text, 
        thread_id = job.thread.get('id'),
        in_reply_to = job.in_reply_to
    )

    ################################################
    #####      PRINT FOR DEBUGGING PURPOSES    #####
    ################################################
    print(f"Now emailing...:\nrecipient: {job.recipient}\nsubject: {job.subject}\nthreadId: {job.thread.get('id')}")
    ################################################
    
    gmail_api.send_email(email = email_draft)
