from datetime import datetime

def convert_time_24_to_12(hour, minute):
    time = datetime.strptime(f"{hour}:{minute}", "%H:%M")
    return time.strftime("%I:%M %p")