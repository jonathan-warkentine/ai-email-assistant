import logging
from logging.handlers import RotatingFileHandler

from config.config_loader import curry_config_parser
from controllers import Email_controller, Scheduling_controller, Job_controller
from services import Gmail_client, Workiz_client, Chatgpt_client

def initialize_logging():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
    return logging

def initialize_configs():
    configs = curry_config_parser()
    return configs

def initialize_clients(configs):
    """Initialize and return all required clients."""
    try:
        # Gmail client initialization
        gmail_config = configs('gmail')
        gmail_client = Gmail_client(gmail_config)

        # ChatGPT and Workiz client initialization
        chatgpt_client = Chatgpt_client(configs('chatgpt'))
        workiz_client = Workiz_client(configs('workiz'))

        return gmail_client, chatgpt_client, workiz_client
    except Exception as e:
        logging.error(f"Failed to initialize clients: {e}")
        raise

def initialize_controllers(gmail_client, chatgpt_client, workiz_client, configs):
    scheduling_ctrl = Scheduling_controller(workiz_client)
    email_ctrl = Email_controller(gmail_client)
    job_ctrl = Job_controller(gmail_client, chatgpt_client, configs)

    return scheduling_ctrl, email_ctrl, job_ctrl