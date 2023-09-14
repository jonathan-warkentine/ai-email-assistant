from datetime import datetime, timedelta

def round_to_nearest_hour(time_obj):
    """Round the time object to the nearest whole hour."""
    return (datetime.combine(datetime.today(), time_obj) + timedelta(minutes=30)).time().replace(minute=0, second=0)