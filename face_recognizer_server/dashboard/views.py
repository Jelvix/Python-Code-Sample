import collections
import datetime

from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination

from django.views.generic.list import ListView

from company.models import Company
from dashboard.models import PersonStatistics
from stuff.models import Person, PersonTracking
from stuff.serializers import PersonTrackingSerializer, ConcretePersonActionHistorySerializer
from django.utils import timezone
from .constants import SECONDS_IN_HOUR, SECONDS_IN_MINUTE
from .serializers import PersonStatisticsSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PersonStatisticsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = PersonStatisticsSerializer

    def get_stats_by_person_id(self, request):
        queryset = PersonStatistics.objects.filter(person__pk=request.GET['person_id']).order_by('-date')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PersonStatisticsSerializer(queryset, many=True)
        return Response(self.get_paginated_response(serializer.data))

    def get_stats_by_company_id(self, request):
        queryset = PersonStatistics.objects.filter(person__company__pk=request.GET['company_id']).order_by('-date')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PersonStatisticsSerializer(queryset, many=True)
        return Response(self.get_paginated_response(serializer.data))


class DashboardListView(ListView):
    model = PersonStatistics

    def get_context_data(self, **kwargs):
        context = get_ctx_for_tracking(6)
        return context


def get_ctx_for_tracking(days):
    """
    :param days: count of wanted previous days
    :return: Context of tracking time, companies and persons for required days
    """

    companies = {}

    for company in Company.objects.all():
        users = collections.OrderedDict()
        persons = Person.active_objects.filter(company=company).order_by('first_name')
        dates = get_dates_by_current_day(days)

        for person in persons:
            users[person.pk] = {person.person_full_name: []}
            for date in dates:
                statics = PersonStatistics.objects.filter(date__date=date, person=person).first()
                if statics is not None:
                    users[person.pk][person.person_full_name].append(statics.tracked_time_as_text)
                else:
                    users[person.pk][person.person_full_name].append("Not generated")

        companies[company] = users

    result = {'dates': dates, 'companies': companies}

    return result


def get_user_tracked_time(person, date):
    """
    :param person: Person object
    :param date: Date for need tracking rime
    :return: hours, minutes, seconds of tracked person's time in office
    """
    sum_time = 0
    tracking_queryset = PersonTracking.objects.filter(action_history__person=person,
                                                      action_history__timestamp__date=date).order_by(
        'action_history__timestamp')

    start_temp_time = None
    stop_temp_time = None

    for action in tracking_queryset:
        if action.action_history.status == 1 and start_temp_time is None:
            start_temp_time = action.action_history.timestamp
        elif action.action_history.status == 2 and stop_temp_time is None:
            stop_temp_time = action.action_history.timestamp

        if start_temp_time is not None and stop_temp_time is not None:
            if stop_temp_time > start_temp_time:
                elapsed_time = stop_temp_time - start_temp_time
                sum_time += elapsed_time.total_seconds()

                start_temp_time = None
                stop_temp_time = None
            else:
                stop_temp_time = None
        else:
            continue

    hours = int(sum_time // SECONDS_IN_HOUR)
    minutes = int((sum_time % SECONDS_IN_HOUR) // SECONDS_IN_MINUTE)
    seconds = int((sum_time % SECONDS_IN_HOUR) % SECONDS_IN_MINUTE)

    return hours, minutes, seconds


def get_dates_by_current_day(count_of_days=6):
    """
    :param count_of_days: count of wanted previous days
    :return: List of the dates that was count_of_days days ago starting from current date
    """
    result = [timezone.now().date() - datetime.timedelta(days=i) for i in range(count_of_days, -1, -1)]
    return result


def update_user_tracked_time(person, date):
    """
    Using for updating time if person doesn't leave office at the end of day. Create action `stop` and attach to this
    action timestamp at the end of the previous day. Create action `start` and attach to this action timestamp at the
    start of the given day.
    
    statuses:
    START_TRACKING = 1
    STOP_TRACKING = 2
    DO_NOTHING = 3
    
    :param person:  Person obj for updating
    :param date: Date of day for updating
    :return: New objects in database
    """
    tracking_queryset = PersonTracking.objects.filter(action_history__person=person,
                                                      action_history__timestamp__date=date.date()).order_by(
        'action_history__timestamp')

    last_action_in_previous_day = tracking_queryset.last()

    if last_action_in_previous_day is not None and last_action_in_previous_day.action_history.status == 1:
        last_time_in_previous_day = datetime.datetime(date.year, date.month, date.day, 23, 59,
                                                      59)
        data_for_creation_in_previous_day = {'person': person.pk, 'status': 2, 'door': None,
                                             'timestamp': last_time_in_previous_day}
        action_history_serializer_in_previous_day = ConcretePersonActionHistorySerializer(
            data=data_for_creation_in_previous_day)

        if action_history_serializer_in_previous_day.is_valid():
            action_history_obj_in_previous_day = action_history_serializer_in_previous_day.save()
            person_tracking_serializer_in_previous_day = PersonTrackingSerializer(
                data={'action_history': action_history_obj_in_previous_day.pk})
            if person_tracking_serializer_in_previous_day.is_valid():
                person_tracking_serializer_in_previous_day.save()

            first_time_in_current_day = datetime.datetime(date.year, date.month, date.day, 0, 0, 0, 1)
            data_for_creation_in_current_day = {'person': person.pk, 'status': 1, 'door': None,
                                                'timestamp': first_time_in_current_day}
            action_history_serializer_in_current_day = ConcretePersonActionHistorySerializer(
                data=data_for_creation_in_current_day)
            if action_history_serializer_in_current_day.is_valid():
                action_history_obj_in_current_day = action_history_serializer_in_current_day.save()
                person_tracking_serializer_in_current_day = PersonTrackingSerializer(
                    data={'action_history': action_history_obj_in_current_day.pk})
                if person_tracking_serializer_in_current_day.is_valid():
                    person_tracking_serializer_in_current_day.save()
            else:
                action_history_serializer_in_current_day.is_valid()
                print(action_history_serializer_in_current_day.errors)
        else:
            action_history_serializer_in_previous_day.is_valid()
            print(action_history_serializer_in_previous_day.errors)


def create_person_statistic_obj_for_yesterday(company):
    """
    Method for creating Person's statistic for previous day

    :param company: Company object
    :return: None
    """
    yesterday = datetime.datetime.now(company.timezone) - datetime.timedelta(days=1)
    persons = company.persons.all().order_by('first_name')

    for person in persons:
        if is_person_stats_created(person, yesterday):
            continue
        else:
            update_user_tracked_time(person, yesterday)
            hours, minutes, seconds = get_user_tracked_time(person, yesterday)
            create_person_statistic_obj(yesterday, person, hours, minutes, seconds)
    return None


def is_person_stats_created(person, timestamp):
    """
    Check if statistic for person already created

    :param person: person
    :param timestamp: timestamp with date for checking
    :return: True of False
    """

    count_of_person_stats_in_specific_day = PersonStatistics.objects.filter(person=person,
                                                                            date__date=timestamp.date()).count()
    if count_of_person_stats_in_specific_day > 0:
        return True
    else:
        return False


def create_person_statistic_obj(date, person, hours, minutes, seconds):
    """
    Method for creating Person statistic by parameters

    :param date: Timestamp of day when person tracking
    :param person: Person obj
    :param hours: Tracked hours
    :param minutes: Tracked minutes
    :param seconds: Tracked seconds
    :return: Created person statistic objects
    """
    tracked_time = datetime.time(hours, minutes, seconds)

    # TODO:
    # Important note:
    # When you try to save something like 2019-02-09 00:18:00.081753+07:00 (timestamp with utc offset +7),
    # django ignore this offset and save it like 2019-02-08 17:18:00.081753+00:00, the we use this variable for creating
    # correct tracking date in database
    date_without_utc_offset = datetime.datetime(date.year, date.month, date.day)

    person_statistic_serializer = PersonStatisticsSerializer(
        data={'date': date_without_utc_offset, 'person': person.pk, 'tracked_time': tracked_time})

    if person_statistic_serializer.is_valid():
        person_statistic_obj = person_statistic_serializer.save()
        return person_statistic_obj
    else:
        print(person_statistic_serializer.is_valid())
        print(person_statistic_serializer.errors)
