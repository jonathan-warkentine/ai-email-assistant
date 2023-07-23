from datetime import datetime
import pytz

def now():
    # Create a timezone object for Eastern Standard Time (EST)
    eastern = pytz.timezone('US/Eastern')

    # Get current date and time
    eastern_datetime = datetime.now(eastern)

    # strftime creates a string from a datetime object
    formatted_now = eastern_datetime.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_now
