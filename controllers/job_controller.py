from utils.convert_string_to_boolean import convert_string_to_boolean
from utils.email_utils import extract_email_address_from_text, is_text_part, extract_last_message_in_thread, extract_message_header_value
from models import Job

class Job_controller:
    def __init__(self, gmail_client, chatgpt_client, configs):
        self.gmail_client = gmail_client
        self.chatgpt_client = chatgpt_client
        self.configs = configs
    
    def generate_jobs_from_threads(self, threads):
        # Prepare thread as conversation for ChatGPT API call ('messages' parameter)
        jobs = list()
        for thread in threads:
            messages = self.gmail_client._parse_thread_for_messages(thread)
            prepared_messages = self.gmail_client._prepare_messages_for_chatgpt(messages=messages)

            # decide if the thread in question regards a job; if not, skip        
            does_thread_regard_job = self._decide_if_messages_regard_job(prepared_messages)
            if not does_thread_regard_job:
                continue

            last_email_in_thread = extract_last_message_in_thread(thread)
            message_id_of_last_email = extract_message_header_value(
                message = last_email_in_thread,
                header_name = 'Message-Id'
            )
            subject_of_last_email = extract_message_header_value(
                message = last_email_in_thread,
                header_name = 'Subject'
            )
            email_address_of_sender_of_last_email = extract_email_address_from_text(
                extract_message_header_value(
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
    
    def _decide_if_messages_regard_job(self, messages):
        triage_incoming_email_prompt = self.configs('chatgpt')('prompts')('triage_email_prompt')
        response = self.chatgpt_client.issue_chatgpt_request(messages, triage_incoming_email_prompt)
        return convert_string_to_boolean(response)
    
    def _prepare_messages_for_chatgpt(self, messages):
        """
        Process a list of email messages fetched from the Gmail API and prepares them 
        in a format suitable for chat. It distinguishes between the 'user' and the 
        'assistant' based on the email sender.
        """
        message_exchange = list()

        for message in messages:
            try:
                sender_email = extract_email_address_from_text(
                    self.extract_message_header_value(
                        message=message,
                        header_name='From'
                    )
                )

                role = 'assistant' if sender_email == self.user else 'user'
                
                parts = message['payload'].get('parts', [])
                
                # First try to find a text/plain part
                text_parts = [part for part in parts if is_text_part(part)]

                if text_parts:
                    # Use only the first text/plain part found
                    message_exchange.extend(self._process_part(text_parts[0], role))
                elif parts:  # If no text/plain part was found, process all other parts
                    for part in parts:
                        message_exchange.extend(self._process_part(part, role))
                else:
                    # If there are no parts, decode the message directly
                    data = message['payload']['body']['data']
                    text = base64.urlsafe_b64decode(data).decode('utf-8')
                    message_exchange.append({"role": role, "content": strip_quoted_text(text)})

            except KeyError:
                continue

        return message_exchange