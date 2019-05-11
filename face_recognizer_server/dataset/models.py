from django.db import models
from django.utils.translation import ugettext_lazy as _
from face_recognizer_server.utils.upload_location import upload_dataset


class Dataset(models.Model):
    version = models.IntegerField(verbose_name=_("Version of dataset"), blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date of training or updating dataset"))
    company = models.ForeignKey('company.Company', verbose_name=_("Foreign key from company to dataset"),
                                related_name='dataset', on_delete=models.CASCADE)
    dataset_file = models.FileField(verbose_name=_('Dataset file'), blank=False, null=False, upload_to=upload_dataset)

    def __str__(self):
        return "{1} {0}".format(self.version, self.company.company_name)
