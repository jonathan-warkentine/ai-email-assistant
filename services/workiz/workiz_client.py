from app_data.data_util import Data_store

import requests

class Workiz_client:
    def __init__(self, config):
        self.api_token = config('credentials')('api_token')
    
    def get_jobs(self):
        try:
            response = requests.get(f'https://api.workiz.com/api/v1/{self.api_token}/job/all/')
            return response.json().get('data')

        except BaseException as e:
            print(f"An error occurred: {e}")

    def get_job(self, job_uuid):
        try:
            response = requests.get(f'https://api.workiz.com/api/v1/{self.api_token}/job/get/{job_uuid}/')
            return response.json()

        except BaseException as e:
            print(f"An error occurred: {e}")
    
    def get_scheduled_appointments(self):
        jobs = self.get_jobs()
        scheduled_appointments = list()
        for job in jobs:
            job_start = job.get('JobDateTime')
            job_end = job.get('JobEndDateTime')
            scheduled_appointments.append({
                'start' : job_start,
                'end' : job_end
            })
        return scheduled_appointments