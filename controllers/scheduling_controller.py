from datetime import datetime, timedelta
from utils.date_time_utils import format_time, format_date_to_month_day, convert_time_24_to_12

class Scheduling_controller:
    def __init__(self, workiz_client):
        self.workiz_client = workiz_client
        self.TIME_FORMAT = "%I:%M %p"
        self.WORK_START = datetime.strptime("8:00 AM", self.TIME_FORMAT).time()
        self.WORK_END = datetime.strptime("6:00 PM", self.TIME_FORMAT).time()


    def get_scheduling_parameters_as_chatgpt_system_prompt(self, workiz_client):
        """
        Get scheduling parameters for chatGPT system prompt.

        :param workiz_client: Client instance for Workiz service
        :return: Dictionary with scheduling parameters
        """
        scheduled_appointments = workiz_client.get_scheduled_appointments()
        availability_string = self._get_availability_string(scheduled_appointments)
        scheduling_parameters = {
            'role': 'system',
            'content': f'Your business hours are 8AM - 6PM Monday through Saturday. Here are your available slots:\n{availability_string}\n\nWhen responding to customers, refer to tomorrow\'s date as "tomorrow", and specify "this week" or "next week" as necessary.'
        }
        return scheduling_parameters

    def _get_availability_string(self, scheduled_appointments):
        """
        Generate availability string based on business hours and provided busy blocks.

        :param scheduled_appointments: List of busy time blocks
        :return: Formatted string indicating availability
        """
        availability = []
        current_datetime = datetime.now()
        two_hours_from_now = current_datetime + timedelta(hours=2)
        
        unique_dates = {format(block.get('start').split()[0]) for block in scheduled_appointments}
        
        for date in sorted(unique_dates):
            if date == current_datetime.strftime('%B %d') and datetime.strptime(self.WORK_END.strftime(self.TIME_FORMAT), self.TIME_FORMAT).time() <= two_hours_from_now.time():
                continue
            
            sorted_times = _get_sorted_times_from_scheduled_appointments(scheduled_appointments, date)
            daily_availability = [f"On {date}:"]  # Starting each date with a header
            available_from = WORK_START
            
            for (start, end) in sorted_times:
                busy_start = datetime.strptime(start, TIME_FORMAT).time()
                if date == current_datetime.strftime('%B %d') and busy_start <= two_hours_from_now.time():
                    continue
                
                # Assuming you've defined the format_time function somewhere
                if available_from != busy_start:
                    daily_availability.append(f"  - Available from: {format_time(available_from)} to {format_time(busy_start)}")
                available_from = datetime.strptime(end, TIME_FORMAT).time()
            
            if available_from != WORK_END:
                daily_availability.append(f"  - Available from: {format_time(available_from)} to {format_time(WORK_END)}")
            
            availability.extend(daily_availability)
        
        return "\n".join(availability)
    
    def _get_sorted_times_from_scheduled_appointments(self, scheduled_appointments, date):
        """
        Get sorted times from provided busy blocks for a given date.

        :param scheduled_appointments: List of busy time blocks
        :param date: Date string for which to fetch sorted times
        :return: Sorted list of start and end times
        """
        times = []
        for block in scheduled_appointments:
            if format_date_to_month_day(block.get('start').split()[0]) == date:
                start = convert_time_24_to_12(*map(int, block.get('start').split()[1].split(":")[:2]))
                end = convert_time_24_to_12(*map(int, block.get('end').split()[1].split(":")[:2]))
                times.append((start, end))
        return sorted(times, key=lambda x: datetime.strptime(x[0], self.TIME_FORMAT))
