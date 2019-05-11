from django.contrib import admin
from .models import PersonStatistics


@admin.register(PersonStatistics)
class PersonStatisticsAdmin(admin.ModelAdmin):
    list_display = ['pk', 'person', 'date', 'tracked_time_as_text']

