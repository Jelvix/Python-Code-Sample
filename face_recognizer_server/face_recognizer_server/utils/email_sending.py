from django.core.mail import send_mail
from django.utils import timezone


def notify_training_completed(start_time):
    message = 'Training start at: {} and end at: {}'.format(start_time, timezone.now())
    send_mail(
        'Training completed',
        message,
        'recognizer@example.com',
        ['timofey.antonenko@jelvix.com', 'andrii.marochkyn@jelvix.com']
    )
