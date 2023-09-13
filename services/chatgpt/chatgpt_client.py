import openai
from utils.date_time_utils.now import now

class Chatgpt_client:
    """
    A client wrapper for interfacing with the ChatGPT API.
    
    Attributes:
        client (openai.Client): The instance of the openai client.
        MODEL (str): Model identifier for the ChatGPT API.
        prompts (dict): Dictionary containing predefined prompts.
        default_system_messages (list): Default system messages for each request.
    """

    def __init__(self, config):
        """
        Initializes the Chatgpt_client with the given configuration.

        Args:
            config (function): A configuration retrieval function.
        """
        self.client = openai
        self.MODEL = config('model')
        self.prompts = config('prompts')
        self.client.organization = config('credentials')('OPENAI_ORG_ID')
        self.client.api_key = config('credentials')('OPENAI_API_KEY')
        self.default_system_messages = self._build_default_system_messages()

    def issue_chatgpt_request(self, messages, custom_system_content):
        """
        Issues a request to ChatGPT with messages and retrieves the API's response.

        Args:
            messages (list): List of previous conversation messages.
            custom_system_content (str): Custom content to append to system messages.

        Returns:
            str: The ChatGPT response.
        """
        messages_with_system_content = self._attach_system_messages_to_message_history(messages, custom_system_content)
        return self._fetch_chatgpt_response(messages_with_system_content)

    def _build_default_system_messages(self):
        """
        Constructs the default system messages to be used in each request.

        Returns:
            list: List of default system messages.
        """
        intro_prompt = self.__build_intro_prompt()
        datetime_system_message = self.__build_datetime_system_message()
        return [intro_prompt, datetime_system_message]

    def __build_intro_prompt(self):
        """
        Creates the introductory system message.

        Returns:
            dict: The intro prompt system message.
        """
        intro_prompt = self.prompts('intro_prompt')
        return self._build_system_message(intro_prompt)

    def __build_datetime_system_message(self):
        """
        Creates a system message with the current date and time.

        Returns:
            dict: The datetime system message.
        """
        now_datetime = now()
        return self._build_system_message(f'Current date and time is {now_datetime}')

    def _attach_system_messages_to_message_history(self, message_history, custom_system_content):
        """
        Appends system messages to the existing message history.

        Args:
            message_history (list): Previous messages in the conversation.
            custom_system_content (str): Custom system message content.

        Returns:
            list: Message history with appended system messages.
        """
        all_system_messages = self.default_system_messages.copy()
        if custom_system_content:
            custom_system_message = self._build_system_message(custom_system_content)
            all_system_messages.append(custom_system_message)
        return all_system_messages + message_history

    def _extract_response_message(self, chatgpt_response):
        """
        Extracts the actual response message from the ChatGPT response.

        Args:
            chatgpt_response (dict): Raw response from ChatGPT.

        Returns:
            str: Extracted response message.
        """
        return chatgpt_response.get('choices')[0].get('message').get('content')

    def _build_system_message(self, content):
        """
        Constructs a system message dictionary.

        Args:
            content (str): Content for the system message.

        Returns:
            dict: System message with given content.
        """
        return {
            'role': 'system',
            'content': content
        }

    def _fetch_chatgpt_response(self, messages_with_system_content):
        """
        Sends a request to ChatGPT API and fetches the response.

        Args:
            messages_with_system_content (list): Message list including system messages.

        Returns:
            str: Response from ChatGPT.
        """
        try:
            response = self.client.ChatCompletion.create(
                model=self.MODEL,
                messages=messages_with_system_content,
                temperature=0
            )
            return self._extract_response_message(response)
        except BaseException as e:
            print("\nERROR fetching ChatGPT response: ", e, "\n")
