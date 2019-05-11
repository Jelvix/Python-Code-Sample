from rest_framework import serializers
from .models import ConcretePersonActionHistory, PersonTracking


class ConcretePersonActionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcretePersonActionHistory
        fields = ['person', 'status', 'door', 'timestamp', 'id']


class PersonTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonTracking
        fields = ['action_history', 'id']
