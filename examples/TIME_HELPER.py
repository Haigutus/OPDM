from datetime import datetime, timedelta
from aniso8601 import parse_duration

now = datetime.now()


def get_year_start(date_time=now):
    year_start = date_time.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    return year_start


def get_month_start(date_time=now):
    month_start = date_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    return month_start


def get_week_start(date_time=now):
    weekday = date_time.weekday()

    day_start = get_day_start(date_time)

    week_start = day_start - timedelta(days=weekday)

    return week_start


def get_day_start(date_time=now):
    day_start = date_time.replace(hour=0, minute=0, second=0, microsecond=0)

    return day_start


def get_hour_start(date_time=now):
    hour_start = date_time.replace(minute=0, second=0, microsecond=0)

    return hour_start


reference_times = {
    "currentHourStart": get_hour_start,
    "currentDayStart": get_day_start,
    "currentWeekStart": get_week_start,
    "currentMonthStart": get_month_start,
    "currentYearStart": get_year_start
}


def timestamp_range(start_date, end_date, iso_duration):
    timestamp_list = []
    timestamp = start_date

    while timestamp <= end_date:
        timestamp_list.append(timestamp)
        timestamp += parse_duration(iso_duration)

    return timestamp_list


