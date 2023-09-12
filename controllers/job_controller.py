from utils.convert_string_to_boolean import convert_string_to_boolean
from utils.email_utils import extract_email_address_from_text
from models import Job

class Job_controller:
    def __init__(self, gmail_client, chatgpt_client):
        self.gmail_client = gmail_client
        self.chatgpt_client = chatgpt_client
    
    def generate_jobs_from_threads(self, threads):
        # Prepare thread as conversation for ChatGPT API call ('messages' parameter)
        jobs = list()
        for thread in threads:
            messages = self.gmail_client.parse_thread_for_messages(thread)
            prepared_messages = self.gmail_client.prepare_messages_for_chatgpt(messages=messages)

            # decide if the thread in question regards a job; if not, skip        
            does_thread_regard_job = convert_string_to_boolean(
                    self.chatgpt_client.decide_if_messages_regard_job(prepared_messages)
                )
            if not does_thread_regard_job:
                continue

            last_email_in_thread = self.gmail_client.extract_last_message_in_thread(thread)
            message_id_of_last_email = self.gmail_client.extract_message_header_value(
                message = last_email_in_thread,
                header_name = 'Message-Id'
            )
            subject_of_last_email = self.gmail_client.extract_message_header_value(
                message = last_email_in_thread,
                header_name = 'Subject'
            )
            email_address_of_sender_of_last_email = extract_email_address_from_text(
                self.gmail_client.extract_message_header_value(
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
            print(f'\n"{subject_of_last_email}" from {email_address_of_sender_of_last_email} (message_id = {message_id_of_last_email})\n')
            ################################################
        return jobs

    def compose_email_response_content(self, jobs, scheduling_parameters, chatgpt_client):
        for job in jobs:
            job.chatgpt_completed_conversation = chatgpt_client.fetch_chatgpt_response(messages = job.conversation, custom_system_content = scheduling_parameters)
        return jobs