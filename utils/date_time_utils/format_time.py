def format_time(time_obj):
    if time_obj.minute == 0:
        return time_obj.strftime('%I %p').lstrip('0')
    else:
        return time_obj.strftime('%I:%M %p').lstrip('0')