from dotenv import load_dotenv
from utils.data_util import Data_store
from utils.now import now

import openai
import os

# Load environment variables
load_dotenv()

class Chatgpt_api:
    def __init__(self, model='gpt-3.5-turbo'):
        self.MODEL = model
        self.client = openai
        self.client.organization = os.getenv('OPENAI_ORG_ID')
        self.client.api_key = os.getenv('OPENAI_API_KEY')
        self.data_store = Data_store('chatgpt/chatgpt_setup.json')

    def fetch_chatgpt_response(self, messages, custom_system_content):
        messages_with_system_content = self.attach_system_content_to_message_history(message_history = messages, custom_system_content = custom_system_content)
        print(messages_with_system_content)
        try:
            return self.client.ChatCompletion.create(
                model = self.MODEL,
                messages = messages_with_system_content,
                temperature=0,
            )
        except BaseException as e:
            print("Error with OpenAI API call: ", e)
    
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
        intro_prompt = self.data_store.read('intro_prompt')
        return self.build_system_message(intro_prompt)
    
    def build_datetime(self):
        now_datetime = now()
        return self.build_system_message(f'Current date and time is {now_datetime}')