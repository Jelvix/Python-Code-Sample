import sys
import os
import pickle

from django.utils import timezone

from company.models import Company
from face_recognizer_server.celery_config import app
from face_recognizer_src.classes.singleton_recognizer import SingletonRecognizer
from stuff.models import Person
from pathlib import Path
from dataset.models import Dataset
from face_recognizer_server.utils.email_sending import notify_training_completed
from django.core.files import File


@app.task(queue="recognizer")
def create_or_update_dataset(person_pk, dict_type):
    """
    A function that creates a task in celery. When admin add a new person's photo or video, the function updates the
    selected dataset or create new if dataset does not exist. After creating or updating the dataset, set the new
    dataset as current for a person's company.

    1. Get the Person object by pk.
    2. The check is this person has a company.
    3. If a person has a company.
        3.1. If the company have the selected dataset, get the path of this dataset.
            3.1.1. The check is a file exist in `path of current dataset`. If the file exists the update current
            dataset and after updating set it as current_dataset for the company. If the file doesn't exist, then
            print an error message.
        3.2 If the company hasn't the dataset, create a new dataset and print notification.
    4. If a person hasn't the company, print error message.


    :param person_pk: Variable for getting company, person photo, person video and latest dataset. Use person pk cause
    celery require json serializable value.
    :param dict_type: Variable for handle different behaviour of creating/updating face encodings dataset.
    :return: None
    """
    person = Person.active_objects.get(pk=person_pk)
    if person.company is not None:

        if person.company.current_dataset:
            path_to_dataset = person.company.current_dataset.dataset_file.path
            if Path(path_to_dataset).is_file():
                update_dataset(dict_type, person)
            else:
                print("Error: dataset file doesn't exist in the destination path", path_to_dataset)
        else:
            print("Notify: create person dataset")
            create_dataset(person)
    else:
        print("Error: a person doesn't have a company")


def update_dataset(dict_type, person):
    """
    Function for updating last dataset of face encodings. Take `dict_type` (Enum) variable for handle different
    behaviour of creating face encodings. Take `person` (stuff.models.Person) variable for getting company by `person`,
    for getting latest dataset by company.

    1. Set `start_executing_time` variable
    2. Get latest face encodings file by person's company into dict variable
    3. Get version variable(int) of last dataset by person's company
    4. Increment dataset version
    5. Create name for updated dataset by incremented version
    6. Set temp path for saving temp dataset for pass it into DataSet model in future
    7. Get the temp dataset data.
    8. Save temp dataset with new data from videos or images to path from the point 6
    9. Read temp dataset file into variable
    10. Create Dataset object in database with latest_dataset_version, person's company and dataset_file
    11. Delete temp dataset file
    12. Print size of latest dataset
    13. Refresh data (face_encodings, face recognizers) in SingletonRecognizer
    14. Send mail about training completed by passing variable `start_executing_time` from the point 1

    :param dict_type: Variable for handle different behaviour of creating face encodings.
    :param person: Variable for getting company, person photo, person video and latest dataset.
    :return: None
    """
    start_executing_time = timezone.now()

    latest_face_encodings = SingletonRecognizer.get_instance().companies_encodings[person.company.pk]

    last_dataset_version = Dataset.objects.filter(company=person.company).last().version
    latest_dataset_version = last_dataset_version + 1

    filename = '{}.dat'.format(latest_dataset_version)
    temp_path = os.path.join("/", filename)

    new_face_encodings = SingletonRecognizer.get_face_encodings_with_indexes_started_by_company_dataset(person,
                                                                                                        dict_type)
    latest_face_encodings.update(new_face_encodings)

    SingletonRecognizer.get_instance().data_worker.create_faces_dataset(latest_face_encodings, temp_path)

    with open(temp_path, 'rb') as f:
        dataset = Dataset.objects.create(version=latest_dataset_version, company=person.company, dataset_file=File(f))
        Company.objects.filter(pk=person.company.pk).update(current_dataset=dataset)
    os.remove(temp_path)
    print("Size after update")
    print(sys.getsizeof(latest_face_encodings))
    SingletonRecognizer.init_singleton_instance()
    notify_training_completed(start_executing_time)


def create_dataset(person):
    """
    Use for creating dataset of face encodings. Take `person` (stuff.models.Person) variable for getting company
    by `person`, for getting latest dataset by company.

    1. Create variable for naming version of dataset
    2. Create name of dataset file
    3. Specify the path for the temp dataset file
    4. Create variables for storing result `result_face_encodings`, images { path_to_photo:person_id },
    video { path_to_video:person_id }
    5. Get the new encodings from images and video.
    6. Add the new encodings from images and frames of video to `result_face_encodings`
    7. Save dataset with result_face_encodings to temp file with path from point 3
    8. Read dataset file from previous step and create Dataset object in database with
    dataset_version, person's company and dataset_file
    9. Remove dataset file from temp path
    10. Refresh data (face_encodings, face recognizers) in SingletonRecognizer

    :param person: Variable for getting company, person photo, person video and creating Dataset object.
    :return: None
    """
    version = 1
    filename = '{}.dat'.format(version)

    temp_path = os.path.join("/", filename)

    result_face_encodings = {}

    new_face_encodings_from_images = SingletonRecognizer.get_face_encodings_with_indexes_started_by_company_dataset(
        person, 'image')
    new_face_encodings_from_video = SingletonRecognizer.get_face_encodings_with_indexes_started_by_company_dataset(
        person, 'video')

    result_face_encodings.update(new_face_encodings_from_images)
    result_face_encodings.update(new_face_encodings_from_video)

    with open(temp_path, 'wb') as f:
        pickle.dump(result_face_encodings, f)

    with open(temp_path, 'rb') as f:
        dataset = Dataset.objects.create(version=version, company=person.company, dataset_file=File(f))
        Company.objects.filter(pk=person.company.pk).update(current_dataset=dataset)
    SingletonRecognizer.init_singleton_instance()
    os.remove(temp_path)
