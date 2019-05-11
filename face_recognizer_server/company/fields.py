import pytz
from timezone_field import TimeZoneField


class AdvancedTimeZoneField(TimeZoneField):
    CHOICES = [
        (pytz.timezone(tz), tz.replace('_', ' '))
        for tz in pytz.all_timezones
    ]
    MAX_LENGTH = 500
