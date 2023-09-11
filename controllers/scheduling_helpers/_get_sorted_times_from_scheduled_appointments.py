from utils.date_time_utils import format_date_to_month_day, convert_time_24_to_12
import datetime

TIME_FORMAT = "%I:%M %p"

def get_sorted_times_from_scheduled_appointments(scheduled_appointments, date):
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
    return sorted(times, key=lambda x: datetime.strptime(x[0], TIME_FORMAT))
