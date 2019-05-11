import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.views import create_person_statistic_obj, is_person_stats_created, update_user_tracked_time, \
    get_user_tracked_time
from stuff.models import Person


class Command(BaseCommand):
    help = 'Generate person stats for previous month'

    def handle(self, *args, **kwargs):
        dates = [timezone.now() - datetime.timedelta(days=i) for i in range(2, 30)]
        for person in Person.objects.all():
            for date in dates:
                if not is_person_stats_created(person, date):
                    update_user_tracked_time(person, date)
                    hours, minutes, seconds = get_user_tracked_time(person, date)
                    create_person_statistic_obj(date, person, hours, minutes, seconds)
