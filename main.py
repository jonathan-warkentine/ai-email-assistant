# External Libraries
from google.auth.transport.requests import Request

# Internal Modules
from config.config_loader import curry_config_parser

from services.chatgpt.chatgpt_client import Chatgpt_client
from services.gmail.gmail_client import Gmail_client
from services.workiz.workiz_client import Workiz_client

from controllers.scheduling_controller import get_scheduling_parameters_as_chatgpt_system_prompt


######################################################################################
#                              Initialize Clients                                    #
######################################################################################
gmail_config = curry_config_parser()('gmail')
gmail_client = Gmail_client(
    credentials_filepath=gmail_config('credentials_filepath') 
    scopes=gmail_config('scopes'),
    user=gmail_config('user'), 
    data_store_filepath=gmail_config('data_store_filepath')
)

chatgpt_client = Chatgpt_client()
workiz_client = Workiz_client()


######################################################################################
#                     Obtain Scheduling Params for ChatGPT Prompt                    #
######################################################################################
get_scheduling_parameters_as_chatgpt_system_prompt(workiz_client)

######################################################################################
#                           FETCH NEW MESSAGES IN GMAIL                              #
######################################################################################
