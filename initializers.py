import logging

from config.config_loader import curry_config_parser
from controllers import Email_controller, Scheduling_controller, Job_controller
from services import Gmail_client, Workiz_client, Chatgpt_client

def initialize_clients():
    """Initialize and return all required clients."""
    try:
        # Gmail client initialization
        gmail_config = curry_config_parser()('gmail')
        gmail_client = Gmail_client(
            credentials_filepath=gmail_config('credentials_filepath'), 
            scopes=gmail_config('scopes'),
            user=gmail_config('user'), 
            data_store_filepath=gmail_config('data_store_filepath')
        )

        # ChatGPT and Workiz client initialization
        chatgpt_client = Chatgpt_client()
        workiz_client = Workiz_client()

        return gmail_client, chatgpt_client, workiz_client
    except Exception as e:
        logging.error(f"Failed to initialize clients: {e}")
        raise

def initialize_controllers(gmail_client, chatgpt_client, workiz_client):
    scheduling_ctrl = Scheduling_controller(workiz_client)
    email_ctrl = Email_controller(gmail_client)
    job_ctrl = Job_controller(gmail_client, chatgpt_client)

    return scheduling_ctrl, email_ctrl, job_ctrl