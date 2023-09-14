from datetime import datetime
from utils import date_time_utils

def render_human_readable(available_slots):
    friendly_slots = {}

    for date, slots in available_slots.items():
        date_key = date.strftime('%B %d')
        formatted_slots = []

        for slot in slots:
            formatted_slots.append(
                f"Available from {date_time_utils.format_time(slot[0])} to {date_time_utils.format_time(slot[1])}"
            )

        friendly_slots[date_key] = formatted_slots

    return friendly_slots
