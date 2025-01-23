import datetime

def unix_timestamp(
    days: int = 0,
    seconds: int = 0,
    microseconds: int = 0,
    milliseconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    weeks: int = 0,
) -> int:
    """
    Get the Unix timestamp for a date in the future
    :param days: The number of days in the future
    :param seconds: The number of seconds in the future
    :param microseconds: The number of microseconds in the future
    :param milliseconds: The number of milliseconds in the future
    :param minutes: The number of minutes in the future
    :param hours: The number of hours in the future
    :param weeks: The number of weeks in the future

    :return: The Unix timestamp for the future date
    """
    out = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
        days,
        seconds,
        microseconds,
        milliseconds,
        minutes,
        hours,
        weeks,
    )
    return int(out.timestamp())