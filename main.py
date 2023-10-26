# External Libraries
import time
import traceback

# Internal Modules
from initializers import initialize_logging, initialize_configs, initialize_clients, initialize_controllers

def main():
    logging = initialize_logging()
    
    # INITIALIZE CONFIGS, CLIENTS, & CONTROLLERS
    configs = initialize_configs()
    gmail_client, chatgpt_client, workiz_client = initialize_clients(configs)
    scheduling_ctrl, email_ctrl, job_ctrl = initialize_controllers(gmail_client, chatgpt_client, workiz_client, configs)

    # Continuous loop for the business logic
    while True:
        try:
            logging.info("Fetching new emails...")
            threads = email_ctrl.process_new_email_threads()

            if threads:
                logging.info("Fetching scheduling parameters...")
                scheduling_parameters = scheduling_ctrl.get_scheduling_parameters()

                logging.info("Generating jobs from threads...")
                jobs = job_ctrl.generate_jobs_from_threads(threads)

                logging.info("Composing email response content...")
                jobs_with_chatgpt_responses = job_ctrl.compose_email_response_content(jobs, scheduling_parameters, chatgpt_client)

                logging.info("Saving email response drafts...")
                email_ctrl.draft_email_responses(jobs_with_chatgpt_responses)

                logging.info("Successful completion of mail sync.")
            else:
                logging.info("NO NEW EMAILS FOUND.")
        except Exception as e:
            logging.error(f"ERROR: {e}")
            logging.error(traceback.format_exc())  # Log the full stack trace
            time.sleep(10)  # Sleep for 10 seconds after an error

        try:
            interval = configs('app_run_interval')
        except:
            interval = 60  # Default to 60 seconds if there's an issue retrieving the interval
            logging.warning(f"Failed to fetch 'app_run_interval'. Defaulting to {interval} seconds.")

        logging.info(f"Waiting {interval} seconds for the next cycle...")
        time.sleep(interval)

if __name__ == "__main__":
    main()
