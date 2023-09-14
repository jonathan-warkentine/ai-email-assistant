from utils import email_utils

class Email_controller:
    def __init__(self, gmail_client):
        self.gmail_client = gmail_client

    def process_new_email_threads(self):
        threads_with_new_messages = self.gmail_client.fetch_threads_with_new_messages()
        threads_awaiting_response = email_utils.filter_threads_awaiting_response(self.gmail_client.user, threads_with_new_messages)

        return threads_awaiting_response

    def draft_email_responses(self, jobs):
        for job in jobs:
            draft = self._create_email_draft_from_job(job)
            self.gmail_client.save_email_draft(draft)

    def _create_email_draft_from_job(self, job):
         return email_utils.compose_email(
                user=self.gmail_client.user,
                recipient=job.recipient,
                subject=job.subject,
                message_text=job.chatgpt_completed_conversation, # assuming this contains the response text
                thread_id=job.thread.get('id'),
                in_reply_to=job.in_reply_to
            )
