def format_time(t):
    formatted_time = t.strftime('%I:%M %p') if t.minute != 0 else t.strftime('%I %p')
    return formatted_time.lstrip('0')  # Remove leading zero if any