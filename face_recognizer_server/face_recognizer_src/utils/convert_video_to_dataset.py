import os

from face_recognizer_src.classes.data_worker import DataWorker
from face_recognizer_src.settings import BASE_PATH
from django.utils import timezone


def train(video_to_user):
    """
    Given a dict of video files and user ids. Make a dataset by detected faces from video.

    :param video_to_user: dict of video and user_id
    :return: Trained dataset
    """

    start_time = timezone.now()

    all_face_encodings = DataWorker.get_face_encodings_from_video_dict(video_to_user)

    DataWorker._save_face_encodings(all_face_encodings, os.path.join(BASE_PATH, 'datasets/dataset_faces.dat'))

    info = 'Training start at: {} and end at: {}'.format(start_time, timezone.now())
    # Print start and end time of training
    print(info)


if __name__ == '__main__':
    # video_to_user_list = DataLoader.get_dict_of_video_and_user_id_in_folder()

    video_to_user_list = {
        'test_video/andry.avi': '7',
        'test_video/andry1.avi': '7',
        'test_video/andry2.avi': '7',
        'test_video/tim.avi': '11',
        'test_video/tim1.avi': '11',
        'test_video/ann.avi': '8',
        'test_video/ann1.avi': '8'
    }
    train(video_to_user_list)
