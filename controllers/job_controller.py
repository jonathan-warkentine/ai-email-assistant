
class Job_controller:
    def __init__(self, gmail_client, chatgpt_client):
        self.gmail_client = gmail_client
        self.chatgpt_client = chatgpt_client
    
    def generate_jobs_from_threads(threads):
        # Prepare thread as conversation for ChatGPT API call ('messages' parameter)
        jobs = list()
        for thread in threads:
            messages = gmail_client.parse_thread_for_messages(thread)
            prepared_messages = gmail_client.prepare_messages_for_chatgpt(messages=messages)

            # decide if the thread in question regards a job; if not, skip        
            does_thread_regard_job = convert_string_to_boolean(
                    chatgpt_client.decide_if_messages_regard_job(prepared_messages)
                )
            if not does_thread_regard_job:
                continue

            last_email_in_thread = gmail_client.extract_last_message_in_thread(thread)
            message_id_of_last_email = gmail_client.extract_message_header_value(
                message = last_email_in_thread,
                header_name = 'Message-Id'
            )
            subject_of_last_email = gmail_client.extract_message_header_value(
                message = last_email_in_thread,
                header_name = 'Subject'
            )
            email_address_of_sender_of_last_email = extract_email_address_from_text(
                gmail_client.extract_message_header_value(
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
