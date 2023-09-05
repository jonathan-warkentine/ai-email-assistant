from google.auth.transport.requests import Request
from collections import defaultdict

from gmail.gmail_api import Gmail_api
from chatgpt.chatgpt_api import Chatgpt_api
from workiz.workiz_api import Workiz_api
from models.job import Job
from utils.extract_email_from_text import extract_email_from_text
from utils.convert_string_to_boolean import convert_string_to_boolean
from utils.convert_time_24_to_12 import convert_time_24_to_12
from datetime import datetime, timedelta

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

WORK_START = datetime.strptime("8:00 AM", "%I:%M %p").time()
WORK_END = datetime.strptime("6:00 PM", "%I:%M %p").time()

def convert_to_readable_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d')

def format_time(t):
    formatted_time = t.strftime('%I:%M %p') if t.minute != 0 else t.strftime('%I %p')
    return formatted_time.lstrip('0')  # Remove leading zero if any

def get_sorted_times_from_busy_blocks(busy_blocks, date):
    times = []
    for block in busy_blocks:
        if convert_to_readable_date(block.get('start').split()[0]) == date:
            start = convert_time_24_to_12(*map(int, block.get('start').split()[1].split(":")[:2]))
            end = convert_time_24_to_12(*map(int, block.get('end').split()[1].split(":")[:2]))
            times.append((start, end))
    return sorted(times, key=lambda x: datetime.strptime(x[0], "%I:%M %p"))

def get_availability_string(busy_blocks):
    availability = []
    current_datetime = datetime.now()
    two_hours_from_now = current_datetime + timedelta(hours=2)
    
    unique_dates = {convert_to_readable_date(block.get('start').split()[0]) for block in busy_blocks}
    
    for date in sorted(unique_dates):
        if date == current_datetime.strftime('%B %d') and datetime.strptime(WORK_END.strftime('%I:%M %p'), "%I:%M %p").time() <= two_hours_from_now.time():
            continue  # Skip today if the business end time is within two hours
        
        sorted_times = get_sorted_times_from_busy_blocks(busy_blocks, date)
        daily_availability = [f"On {date}:"]  # Starting each date with a header
        available_from = WORK_START
        
        for (start, end) in sorted_times:
            busy_start = datetime.strptime(start, "%I:%M %p").time()
            if date == current_datetime.strftime('%B %d') and busy_start <= two_hours_from_now.time():
                continue  # Skip time slots that are within two hours for today
            
            if available_from != busy_start:
                daily_availability.append(f"  - Available from: {format_time(available_from)} to {format_time(busy_start)}")
            available_from = datetime.strptime(end, "%I:%M %p").time()
        
        if available_from != WORK_END:
            daily_availability.append(f"  - Available from: {format_time(available_from)} to {format_time(WORK_END)}")
        
        availability.extend(daily_availability)
    
    return "\n".join(availability)

availability_string = get_availability_string(busy_blocks)

scheduling_parameters = {
    'role' : 'system',
    'content' : f'Your business hours are 8AM - 6PM Monday through Saturday. Here are your available slots:\n{availability_string}\n\nWhen responding to customers, refer to tomorrow\'s date as "tomorrow", and specify "this week" or "next week" as necessary.'
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
    messages_regard_job_chatgpt_response = chatgpt_api.decide_if_messages_regard_job(prepared_messages)
    messages_regard_job_as_boolean = convert_string_to_boolean(messages_regard_job_chatgpt_response.get('choices')[0].get('message').get('content'))

    if messages_regard_job_as_boolean == False:
        continue

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
