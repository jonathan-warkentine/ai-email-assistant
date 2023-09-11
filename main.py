# External Libraries
from google.auth.transport.requests import Request
import time
import logging

# Internal Modules
from initializers import initialize_clients, initialize_controllers

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')


def main():
    # Initialize clients
    gmail_client, chatgpt_client, workiz_client = initialize_clients()

    # Initialize controllers
    scheduling_ctrl, email_ctrl, job_ctrl = initialize_controllers(gmail_client, chatgpt_client, workiz_client)

    return
    # Continuous loop for business logic
    while True:
        try:
            logging.info("Fetching scheduling parameters...")
            scheduling_parameters = scheduling_ctrl.get_scheduling_parameters_as_chatgpt_system_prompt()
            
            logging.info("Generating jobs from threads...")
            jobs = job_ctrl.generate_jobs_from_threads(scheduling_parameters)
            
            logging.info("Drafting email responses...")
            email_ctrl.draft_responses(jobs)

            logging.info("Business logic executed successfully. Waiting for the next cycle...")
        except Exception as e:
            logging.error(f"\nERROR during business logic execution: {e}\n")
        
        time.sleep(300)

if __name__ == "__main__":
    main()
