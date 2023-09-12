from utils.date_time_utils.now import now

import openai
import os

class Chatgpt_client:
    def __init__(self, config):
        self.client = openai
        self.MODEL = config('model')
        self.prompts = config('prompts', return_dicts=True)
        self.client.organization = config('credentials')('OPENAI_ORG_ID')
        self.client.api_key = config('credentials')('OPENAI_API_KEY')

    def fetch_chatgpt_response(self, messages, custom_system_content):
        messages_with_system_content = self.attach_system_content_to_message_history(message_history = messages, custom_system_content = custom_system_content)
        try:
            response = self.client.ChatCompletion.create(
                model = self.MODEL,
                messages = messages_with_system_content,
                temperature=0,
            )
            return self.extract_response_message(response)
        except BaseException as e:
            print("\nERROR fetching ChatGPT response: ", e, "\n")

    def decide_if_messages_regard_job(self, messages):
        triage_incoming_email_prompt = self.prompts.get('triage_email_prompt')
        system_message = self.build_system_message(content=triage_incoming_email_prompt)
        combined_system_prompt_and_message_history = [system_message] + messages
        try:
            response = self.client.ChatCompletion.create(
                model = self.MODEL,
                messages = combined_system_prompt_and_message_history,
                temperature=0,
            )
            return self.extract_response_message(response)
        except BaseException as e:
            print("\nERROR fetching ChatGPT response for message triage: ", e, "\n")

    def attach_system_content_to_message_history(self, message_history, custom_system_content):
        all_system_content = self.build_system_content(custom_system_content = custom_system_content)
        combined_message_history_and_system_content = all_system_content + message_history
        return combined_message_history_and_system_content
    
    def build_system_content(self, custom_system_content):
        intro_prompt = self.build_intro_prompt()
        datetime = self.build_datetime()
        return [intro_prompt, datetime, custom_system_content]

    def build_system_message(self, content):
        return {
            'role' : 'system',
            'content' : content,
        }
    
    def build_intro_prompt(self):
        intro_prompt = self.prompts.get('intro_prompt')
        return self.build_system_message(intro_prompt)
    
    def build_datetime(self):
        now_datetime = now()
        return self.build_system_message(f'Current date and time is {now_datetime}')
    
    def extract_response_message(self, chatgpt_response):
        return chatgpt_response.get('choices')[0].get('message').get('content')