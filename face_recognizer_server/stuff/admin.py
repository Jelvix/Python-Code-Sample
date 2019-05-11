from django.contrib import admin
from .models import Person, PersonPhoto, PersonVideo, ConcretePersonActionHistory, PersonTracking


@admin.register(PersonPhoto)
class PersonPhotoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'person', 'photo']
    search_fields = ['person__first_name', 'person__last_name']
    list_filter = ['person__first_name', 'person__last_name']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['pk', 'person_full_name', 'company']
    search_fields = ['first_name', 'last_name', 'company__company_name']
    list_filter = ['company__company_name']


@admin.register(PersonVideo)
class PersonVideoAdmin(admin.ModelAdmin):
    list_display = ['pk', 'person', 'uploaded_video_file']
    search_fields = ['person__first_name', 'person__last_name']
    list_filter = ['person__first_name', 'person__last_name']


@admin.register(ConcretePersonActionHistory)
class ConcretePersonActionHistoryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'person', 'timestamp', 'status', 'file', 'door']
    search_fields = ['person__first_name', 'person__last_name']
    list_filter = ['person__first_name', 'person__last_name']


@admin.register(PersonTracking)
class PersonTrackingAdmin(admin.ModelAdmin):
    list_display = ['pk', 'action_history']

