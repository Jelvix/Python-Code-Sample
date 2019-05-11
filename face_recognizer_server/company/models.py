from django.db import models
from django.utils.translation import ugettext_lazy as _
from company.fields import AdvancedTimeZoneField


class Company(models.Model):
    company_name = models.CharField(verbose_name=_('Company name'), max_length=150)
    timezone = AdvancedTimeZoneField(verbose_name=_('Company timezone'), default='Europe/London')
    current_dataset = models.OneToOneField('dataset.Dataset', verbose_name=_("Using dataset"), blank=True, null=True,
                                           on_delete=models.SET_NULL, related_name="used_dataset")
    tolerance = models.FloatField(verbose_name=_('Tolerance'), blank=False, null=False, default=0.4)

    def __str__(self):
        return self.company_name


class Door(models.Model):
    START_TRACKING = 1
    STOP_TRACKING = 2
    DO_NOTHING = 3

    ACTION_STATUS_CHOICES = (
        (START_TRACKING, _('Start tracking')),
        (STOP_TRACKING, _('Stop tracking')),
        (DO_NOTHING, _('Nothing')),
    )

    name = models.CharField(verbose_name=_('Door title'), max_length=150)
    company = models.ForeignKey('company.Company', verbose_name=_('Company'), blank=True, null=True,
                                on_delete=models.CASCADE)
    allowed_person = models.ManyToManyField('stuff.Person', verbose_name=_('People who are allowed'), blank=True)
    status = models.PositiveSmallIntegerField(verbose_name=_('Status'),
                                              choices=ACTION_STATUS_CHOICES, default=DO_NOTHING)

    def __str__(self):
        return self.name
