from django.utils import timezone


current_timestamp = timezone.now()


def upload_photo_of_person(instance, filename):
    return "face_recognizer_src/persons_photos/{0}/{1}".format(instance.person.pk, filename)


def upload_video_of_person(instance, filename):
    return "face_recognizer_src/persons_video/{0}/{1}".format(instance.person.pk, filename)


def upload_temp_photo_of_person(instance, filename):
    return "face_recognizer_src/temp_photos/{0}/{1}".format(current_timestamp.strftime('%Y-%m-%d'), filename)


def upload_dataset(instance, filename):
    return "dataset/datasets/{0}/{1}".format(instance.company.pk, filename)
