class Email_controller:
    def __init__(self, gmail_client):
        self.gmail_client = gmail_client

    def process_new_email_threads(gmail_client):
        threads_with_new_messages = gmail_client.fetch_threads_with_new_messages()
        threads_awaiting_response = gmail_client.filter_threads_awaiting_response(threads_with_new_messages)

        return threads_awaiting_response

    def draft_responses(jobs, scheduling_parameters, chatgpt_client, gmail_client):
        for job in jobs:
            chatgpt_response = chatgpt_client.fetch_chatgpt_response(messages = job.conversation, custom_system_content = scheduling_parameters)
            email_draft = gmail_client.compose_email(
                recipient = job.recipient, 
                subject = job.subject, 
                message_text = chatgpt_response, 
                thread_id = job.thread.get('id'),
                in_reply_to = job.in_reply_to
            )
            gmail_client.save_email_draft(email_draft)
