from django.db import models
from django.utils.translation import ugettext_lazy as _


class PersonStatistics(models.Model):
    person = models.ForeignKey('stuff.Person', verbose_name=_('Person'), blank=False, null=False,
                               on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name=_('Date of tracked time'))
    tracked_time = models.TimeField(verbose_name=_("Person's tracking time"))

    def __str__(self):
        return "{} {}".format(self.person, self.date)

    @property
    def tracked_time_as_text(self):
        return self.tracked_time.strftime('hours: %H, minutes: %M, seconds: %S')
