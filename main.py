from google.auth.transport.requests import Request
from collections import defaultdict

from gmail.gmail_api import Gmail_api
from chatgpt.chatgpt_api import Chatgpt_api
from workiz.workiz_api import Workiz_api
from models.job import Job
from utils.extract_email_from_text import extract_email_from_text

######################################################################################
#                          Initialize our Gmail Client                               #
######################################################################################
gmail_api = Gmail_api(
    credentials_file_path='gmail/service_account_key.json', 
    scopes=['https://mail.google.com/'], 
    user='automation@topdawgjunkremoval.com', 
    data_store_filepath='./gmail/gmail.json'
)

######################################################################################
#                             Initialize our OpenAI Client                           #
######################################################################################
chatgpt_api = Chatgpt_api()

######################################################################################
#                             Initialize our Workiz Client                           #
######################################################################################
workiz_api = Workiz_api()


######################################################################################
#                     Obtain Scheduling Params for ChatGPT Prompt                    #
######################################################################################
busy_blocks = workiz_api.get_busy_blocks()

consolidated_blocks = defaultdict(dict)

for busy_block in busy_blocks:
    date = busy_block.get('start').split()[0]
    start_time = ":".join(busy_block.get('start').split()[1].split(":")[:2])
    end_time = ":".join(busy_block.get('end').split()[1].split(":")[:2])
    
    consolidated_blocks[date][start_time] = end_time

# Merge logic
for date, blocks in consolidated_blocks.items():
    keys = sorted(blocks.keys())
    i = 0
    while i < len(keys) - 1:
        current_end = blocks[keys[i]]
        next_start = keys[i + 1]

        if current_end == next_start:
            blocks[keys[i]] = blocks[next_start]
            del blocks[next_start]
            keys = sorted(blocks.keys())
        else:
            i += 1

ai_readable_strings = []
for date in sorted(consolidated_blocks.keys()):
    time_strings = [f"{start} to {consolidated_blocks[date][start]}" for start in sorted(consolidated_blocks[date])]
    ai_readable_strings.append(f"On {date}, busy from: {' and '.join(time_strings)}")

ai_readable_string = ". ".join(ai_readable_strings)

scheduling_parameters = {
    'role' : 'system',
    'content' : f'Your business hours are 8AM - 6PM Monday through Saturday. Customers have already booked appointments with you during the following slots: {ai_readable_string}. DO NOT DOUBLE BOOK CUSTOMERS DURING THESE SLOTS. Please use time and date formats that will feel natural to our working class customers.'
}

######################################################################################
#                           FETCH NEW MESSAGES IN GMAIL                              #
######################################################################################
threads_with_new_messages = gmail_api.fetch_threads_with_new_messages()
threads_needing_response = gmail_api.filter_threads_needing_response(threads_with_new_messages)

# Prepare thread as conversation for ChatGPT API call ('messages' parameter)
jobs = list()
for thread in threads_needing_response:
    messages = gmail_api.parse_thread_for_messages(thread)
    prepared_messages = gmail_api.prepare_messages_for_chatgpt(messages=messages)
    messages_regard_job = chatgpt_api.decide_if_messages_regard_job(prepared_messages)
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
        conversation = prepared_messages, 
        thread = thread,
        in_reply_to = message_id_of_last_email
    )
    jobs.append(job)
    ################################################
    #####      PRINT FOR DEBUGGING PURPOSES    #####
    ################################################
    print(f'\n"{subject_of_last_email}" from {email_address_of_sender_of_last_email} (message_id = {message_id_of_last_email})')
    ################################################

for job in jobs:
    chatgpt_response = chatgpt_api.fetch_chatgpt_response(messages = job.conversation, custom_system_content = scheduling_parameters)
    message_text = chatgpt_response.get('choices')[0].get('message').get('content')
    email_draft = gmail_api.compose_email(
        recipient = job.recipient, 
        subject = job.subject, 
        message_text = message_text, 
        thread_id = job.thread.get('id'),
        in_reply_to = job.in_reply_to
    )
    gmail_api.save_email_draft(email_draft)
