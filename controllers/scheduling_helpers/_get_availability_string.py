from datetime import datetime, timedelta

from controllers.scheduling_helpers import _get_sorted_times_from_scheduled_appointments
from utils.date_time_utils import format_time

TIME_FORMAT = "%I:%M %p"
WORK_START = datetime.strptime("8:00 AM", TIME_FORMAT).time()
WORK_END = datetime.strptime("6:00 PM", TIME_FORMAT).time()

def get_availability_string(scheduled_appointments):
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
        if date == current_datetime.strftime('%B %d') and datetime.strptime(WORK_END.strftime(TIME_FORMAT), TIME_FORMAT).time() <= two_hours_from_now.time():
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