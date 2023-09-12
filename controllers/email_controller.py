class Email_controller:
    def __init__(self, gmail_client):
        self.gmail_client = gmail_client

    def process_new_email_threads(self):
        threads_with_new_messages = self.gmail_client.fetch_threads_with_new_messages()
        threads_awaiting_response = self.gmail_client.filter_threads_awaiting_response(threads_with_new_messages)

        return threads_awaiting_response

    def draft_email_responses(self, jobs):
        for job in jobs:
            draft = self._create_email_draft_from_job(job)
            self.gmail_client.save_email_draft(draft)

    def _create_email_draft_from_job(self, job):
         return self.gmail_client.compose_email(
                recipient=job.recipient,
                subject=job.subject,
                message_text=job.chatgpt_completed_conversation, # assuming this contains the response text
                thread_id=job.thread.get('id'),
                in_reply_to=job.in_reply_to
            )
