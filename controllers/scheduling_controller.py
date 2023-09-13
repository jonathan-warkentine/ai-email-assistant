from datetime import datetime, timedelta
from utils import date_time_utils

class Scheduling_controller:
    def __init__(self, workiz_client):
        self.workiz_client = workiz_client
        self.TIME_FORMAT = "%I:%M %p"
        self.WORK_START = datetime.strptime("8:00 AM", self.TIME_FORMAT).time()
        self.WORK_END = datetime.strptime("6:00 PM", self.TIME_FORMAT).time()

    def get_scheduling_parameters(self):
        """
        Get scheduling parameters for chatGPT system prompt.

        :return: Dictionary with scheduling parameters
        """
        scheduled_appointments = self.workiz_client.get_scheduled_appointments()
        print(scheduled_appointments)
        availability_string = self._get_availability_string(scheduled_appointments)
        scheduling_parameters = f'Your business hours are 8AM - 6PM Monday through Saturday. Here are your available slots:\n{availability_string}\n\nWhen responding to customers, refer to tomorrow\'s date as "tomorrow", and specify "this week" or "next week" as necessary.'
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

        unique_dates = {block.get('start').split()[0] for block in scheduled_appointments}

        for date in sorted(unique_dates):
            formatted_date = date_time_utils.format_date_to_month_day(date)
            
            # Exclude times for today that are in the past or less than 2 hours from now
            if formatted_date == current_datetime.strftime('%B %d') and datetime.combine(current_datetime.date(), self.WORK_END) <= two_hours_from_now:
                continue

            sorted_times = self._get_sorted_times_from_scheduled_appointments(scheduled_appointments, date)

            daily_availability = [f"On {formatted_date}:"]  # Starting each date with a header
            
            # Start by assuming the entire work day is free.
            free_times = [(self.WORK_START, self.WORK_END)]

            for (start, end) in sorted_times:
                busy_start = datetime.strptime(start, self.TIME_FORMAT).time()
                busy_end = datetime.strptime(end, self.TIME_FORMAT).time()
                
                new_free_times = []

                for (free_start, free_end) in free_times:
                    # If the busy time doesn't overlap with this free time, keep it as it is.
                    if busy_end <= free_start or busy_start >= free_end:
                        new_free_times.append((free_start, free_end))
                    else:
                        # Otherwise, split the free time around the busy time.
                        if free_start < busy_start:
                            new_free_times.append((free_start, busy_start))
                        if free_end > busy_end:
                            new_free_times.append((busy_end, free_end))
                
                free_times = new_free_times

            for (free_start, free_end) in free_times:
                daily_availability.append(f"  - Available from: {date_time_utils.format_time(free_start)} to {date_time_utils.format_time(free_end)}")
            
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
            if date == block.get('start').split()[0]:  # compare raw dates
                start = date_time_utils.convert_time_24_to_12(*map(int, block.get('start').split()[1].split(":")[:2]))
                end = date_time_utils.convert_time_24_to_12(*map(int, block.get('end').split()[1].split(":")[:2]))
                times.append((start, end))
        return sorted(times, key=lambda x: datetime.strptime(x[0], self.TIME_FORMAT))
