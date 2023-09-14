from datetime import datetime, timedelta
from utils import date_time_utils

class Scheduling_controller:
    TIME_FORMAT = "%I:%M %p"
    WORK_START = datetime.strptime("8:00 AM", TIME_FORMAT).time()
    WORK_END = datetime.strptime("6:00 PM", TIME_FORMAT).time()

    def __init__(self, workiz_client):
        self.workiz_client = workiz_client

    def get_scheduling_parameters(self):
        scheduled_appointments = self.workiz_client.get_scheduled_appointments()
        available_slots = self._derive_availability(scheduled_appointments)
        formatted_slots = date_time_utils.render_human_readable(available_slots)
        availabilities_as_string = date_time_utils.generate_string_output(formatted_slots)
        
        return f'Your business hours are 8AM - 6PM Monday through Saturday. Here are your available slots:\n{availabilities_as_string}\n\nWhen responding to customers, refer to tomorrow\'s date as "tomorrow", and specify "this week" or "next week" as necessary.'

    def _derive_availability(self, scheduled_appointments, days_ahead=14):
        start_date = datetime.now().date()
        return {date: self.calculate_free_times(self.get_todays_appointments(scheduled_appointments, date)) for date in self._generate_date_range(start_date, days_ahead)}

    def _generate_date_range(self, start_date, days_ahead):
        return [start_date + timedelta(days=i) for i in range(days_ahead)]

    def get_todays_appointments(self, all_appointments, date):
        return [block for block in all_appointments if datetime.strptime(block['start'], "%Y-%m-%d %H:%M:%S").date() == date]

    def calculate_free_times(self, todays_appointments):
        if not todays_appointments:
            return [(self.WORK_START, self.WORK_END)]

        sorted_appointments = sorted(todays_appointments, key=lambda x: x['start'])
        free_times = [(self.WORK_START, self.WORK_END)]
        
        for block in sorted_appointments:
            busy_start_time = datetime.strptime(block['start'], "%Y-%m-%d %H:%M:%S").time()
            busy_end_time = datetime.strptime(block['end'], "%Y-%m-%d %H:%M:%S").time()

            busy_start = date_time_utils.round_to_nearest_hour(busy_start_time)
            busy_end = date_time_utils.round_to_nearest_hour(busy_end_time)
            
            free_times = self._update_free_times(free_times, busy_start, busy_end)
            
        return free_times

    def _update_free_times(self, free_times, busy_start, busy_end):
        new_free_times = []
        for (free_start, free_end) in free_times:
            if busy_end <= free_start or busy_start >= free_end:
                new_free_times.append((free_start, free_end))
            else:
                if free_start < busy_start:
                    new_free_times.append((free_start, busy_start))
                if free_end > busy_end:
                    new_free_times.append((busy_end, free_end))
        return new_free_times
