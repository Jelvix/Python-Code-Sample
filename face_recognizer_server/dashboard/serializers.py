from rest_framework import serializers
from .models import PersonStatistics


class PersonStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonStatistics
        fields = ['person', 'date', 'tracked_time']
