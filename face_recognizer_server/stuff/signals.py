from django.db import transaction
from face_recognizer_server.utils.dict_type import DictType


def update_dataset_by_video_signal(sender, instance, **kwargs):
    from .tasks import create_or_update_dataset
    transaction.on_commit(lambda:
                          create_or_update_dataset.delay(person_pk=instance.person.pk, dict_type=DictType.video.value))


def update_dataset_by_image_signal(sender, instance, **kwargs):
    from .tasks import create_or_update_dataset
    transaction.on_commit(lambda:
                          create_or_update_dataset.delay(person_pk=instance.person.pk, dict_type=DictType.image.value))
