from stuff.models import PersonPhoto, PersonVideo
from company.models import Company

from face_recognizer_server.utils.dict_type import DictType
from face_recognizer_src.classes.face_recognizer import FaceRecognizer
from face_recognizer_src.classes.frame_adapter import FrameAdapter
from face_recognizer_src.classes.data_worker import DataWorker


class SingletonRecognizer:
    """
    Class for face detection, face recognition, creating/updating dataset of face encodings, processing image.
    This singleton for using a new face_encoding dataset after training completed without restarting web server.

    Some hardcoded params:
    `resize_coef`: Resize frame of video to `resize_coef` size for faster face recognition processing, but lower
    accuracy
    """

    class __SingletonRecognizer:
        def __init__(self):
            self.companies_encodings = init_companies_face_encodings()
            self.companies_recognizers = init_companies_face_recognizer()
            self.frame_adapter = FrameAdapter(resize_coef=1)
            self.data_worker = DataWorker

        def __str__(self):
            return repr(self)

    __instance = None

    @staticmethod
    def get_instance():
        if not SingletonRecognizer.__instance:
            return SingletonRecognizer.init_singleton_instance()
        else:
            return SingletonRecognizer.__instance

    @staticmethod
    def init_singleton_instance():
        """
        Method for creating/refreshing recognizer object

        :return: return SingletonRecognizer.__instance
        """

        SingletonRecognizer.__instance = SingletonRecognizer.__SingletonRecognizer()
        SingletonRecognizer.__instance = SingletonRecognizer.__SingletonRecognizer()
        return SingletonRecognizer.__instance

    @staticmethod
    def get_face_encodings_with_indexes_started_by_company_dataset(person, dict_type):
        """
        Method for getting face encodings with indexes started by existing face encodings

        1. Get current company's face encodings
        2. We check is a variable `dict_type` an image or video
            2.1 If dict_type is the image
                2.1.1 Get all new photos of this person into dict { path_to_photo:person_id }
                2.1.2 Set status `is_new=False` to all new photos of this person
                2.1.3 Create encodings(dict) for all person's new photo
                2.1.4 Add new encodings from images to latest face encodings
            2.2 Else if dict_type is video
                2.2.1 Get all new videos of this person into dict { path_to_video:person_id }
                2.2.2 Set status `is_new=False` to all new videos of this person
                2.2.3 Create encodings(dict) for all person's new video
                2.2.4 Add new encodings from frames of video to latest face encodings

        :param person: (stuff.Person object)
        :param dict_type: ('video' or 'image' string) type of source for creating face_encodings
        :return: face encodings for creating new dataset
        """

        if not SingletonRecognizer.__instance:
            SingletonRecognizer.init_singleton_instance()

        company_face_encodings_data = SingletonRecognizer.__instance.companies_encodings[person.company.pk]

        data_dict = {}

        if dict_type == DictType.image.value:
            data_model = PersonPhoto
            data_attribute = 'photo'
            data_method = SingletonRecognizer.__instance.data_worker.get_face_encodings_from_image_dict
        elif dict_type == DictType.video.value:
            data_model = PersonVideo
            data_attribute = 'uploaded_video_file'
            data_method = SingletonRecognizer.__instance.data_worker.get_face_encodings_from_video_dict

        for person_data in data_model.objects.filter(person=person, is_new=True):
            data_dict[str(getattr(person_data, data_attribute).path)] = int(person_data.person.pk)
            data_model.objects.filter(id=person_data.id).update(is_new=False)

        return data_method(data_dict, face_encodings_data=company_face_encodings_data)


def init_companies_face_encodings():
    result = {}
    for company in Company.objects.all():
        if company.current_dataset is not None:
            result[company.pk] = DataWorker.load_face_encodings(company.current_dataset.dataset_file.path)
        else:
            print("Error, company {} hasn't selected dataset for using".format(company))

    return result


def init_companies_face_recognizer():
    result = {}
    for company in Company.objects.all():
        if company.current_dataset is not None:
            result[company.pk] = FaceRecognizer(
                DataWorker.load_face_encodings(company.current_dataset.dataset_file.path), tolerance=company.tolerance)
        else:
            print("Error, company {} hasn't selected dataset for using".format(company))

    return result
