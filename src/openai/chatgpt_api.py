from dotenv import load_dotenv

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

    def fetch_chatgpt_response(self, messages):
        response = None
        try:
            response = self.client.ChatCompletion.create(
                model = self.MODEL,
                messages = messages,
                temperature=0,
            )
        except BaseException as e:
            print("Error with OpenAI API call: ", e)
        
        return response