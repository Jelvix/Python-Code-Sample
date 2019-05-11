from django.db import models


class PersonManager(models.Manager):
    def get_queryset(self):
        return super(PersonManager, self).get_queryset().filter(is_active=True)
