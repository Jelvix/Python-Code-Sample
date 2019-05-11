from django.db.models.signals import post_save
from django.db import models
from django.utils.translation import ugettext_lazy as _
from face_recognizer_server.utils.upload_location import upload_photo_of_person, upload_temp_photo_of_person, \
    upload_video_of_person
from stuff.managers import PersonManager
from .signals import update_dataset_by_image_signal, update_dataset_by_video_signal


class Person(models.Model):
    first_name = models.CharField(verbose_name=_('First name'), max_length=50)
    last_name = models.CharField(verbose_name=_('Last name'), max_length=50)
    company = models.ForeignKey('company.Company', verbose_name=_('Company'), blank=False, null=True,
                                on_delete=models.SET_NULL, related_name='persons')
    is_active = models.BooleanField(verbose_name=_('Is this person active'), blank=False, null=False, default=True)

    objects = models.Manager()
    active_objects = PersonManager()

    def __str__(self):
        if self.company is not None:
            return 'Person (id = {3}): {1} {2}, Company: {0}'.format(self.company.company_name, self.first_name,
                                                                     self.last_name,
                                                                     self.pk)
        else:
            return 'Person (id = {2}): {0} {1}'.format(self.first_name, self.last_name, self.pk)

    @property
    def person_full_name(self):
        return "{} {}".format(self.first_name, self.last_name)


class PersonPhoto(models.Model):
    photo = models.ImageField(verbose_name=_('Photo'), blank=False, null=False, upload_to=upload_photo_of_person)
    person = models.ForeignKey('stuff.Person', verbose_name=_('Person'), blank=True, null=True,
                               on_delete=models.CASCADE)
    is_new = models.BooleanField(verbose_name=_('Is this photo new'), blank=False, null=False, default=True)

    def __str__(self):
        return self.photo.url


class PersonVideo(models.Model):
    uploaded_video_file = models.FileField(verbose_name=_('Video'), blank=False, null=False,
                                           upload_to=upload_video_of_person)
    person = models.ForeignKey('stuff.Person', verbose_name=_('Person'), blank=True, null=True,
                               on_delete=models.CASCADE)
    is_new = models.BooleanField(verbose_name=_('Is this video new'), blank=False, null=False, default=True)

    def __str__(self):
        return self.uploaded_video_file.url


class ConcretePersonActionHistory(models.Model):
    """
    Model for logging a time when person come in and come out
    """

    START_TRACKING = 1
    STOP_TRACKING = 2
    DO_NOTHING = 3

    ACTION_STATUS_CHOICES = (
        (START_TRACKING, _('Start tracking')),
        (STOP_TRACKING, _('Stop tracking')),
        (DO_NOTHING, _('Nothing')),
    )

    person = models.ForeignKey('stuff.Person', verbose_name=_('Person'), on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    status = models.PositiveSmallIntegerField(verbose_name=_('Status'),
                                              choices=ACTION_STATUS_CHOICES, default=DO_NOTHING)
    file = models.ImageField(blank=True, null=True, upload_to=upload_temp_photo_of_person)
    door = models.ForeignKey('company.Door', verbose_name=_('Door'), blank=True, null=True,
                             on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=['-timestamp', ]),
        ]

    def __str__(self):
        return "{} {}".format(self.pk, self.person)


class PersonTracking(models.Model):
    action_history = models.ForeignKey('stuff.ConcretePersonActionHistory',
                                       verbose_name=_('Action history'), on_delete=models.CASCADE)

    def __str__(self):
        return "{} {}".format(self.action_history.person, self.action_history.status)


post_save.connect(update_dataset_by_image_signal, sender=PersonPhoto)
post_save.connect(update_dataset_by_video_signal, sender=PersonVideo)
