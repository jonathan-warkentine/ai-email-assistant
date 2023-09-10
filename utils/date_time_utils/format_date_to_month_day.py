from datetime import datetime

def format_date_to_month_day(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d')