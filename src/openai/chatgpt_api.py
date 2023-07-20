from dotenv import load_dotenv
from src.utils.data_util import Data_store

import openai
import os

# Load environment variables
load_dotenv()

class ChatGPT_API:
    def __init__(self, model='gpt-3.5-turbo'):
        self.MODEL = model
        self.client = openai
        self.client.organization = os.getenv('OPENAI_ORG_ID')
        self.client.api_key = os.getenv('OPENAI_API_KEY')
        self.data_store = Data_store('src/openai/openai_setup.json')

    def fetch_chatgpt_response(self, messages):
        messages_with_system_content = self.attach_system_content_to_messages(messages = messages)
        try:
            return self.client.ChatCompletion.create(
                model = self.MODEL,
                messages = messages_with_system_content,
                temperature=0,
            )
        except BaseException as e:
            print("Error with OpenAI API call: ", e)
    
    def attach_system_content_to_messages(self, messages):
        prompt = self.data_store.read('system_content')
        system_content = {
            "role" : "system",
            "content" : prompt
        }

        messages.insert(0, system_content)
        return messages