import pickle
import os
import face_recognition
import cv2

from face_recognizer_src.settings import BASE_PATH, PERSONS_VIDEO_PATH, PERSONS_PHOTO_PATH
from face_recognizer_src.classes.face_data_helper import FaceDataHelper
from face_recognizer_src.classes.frame_processor import FrameProcessor


class DataWorker:
    @staticmethod
    def create_faces_dataset(face_encodings, full_path=os.path.join(BASE_PATH, 'datasets/dataset_faces.dat')):
        DataWorker._save_face_encodings(face_encodings, full_path)
        return face_encodings

    @staticmethod
    def load_face_encodings(full_path=os.path.join(BASE_PATH, 'datasets/dataset_faces.dat')):
        with open(full_path, 'rb') as f:
            all_face_encodings = pickle.load(f)
        return all_face_encodings

    @staticmethod
    def get_face_encodings_from_local_images(path=PERSONS_PHOTO_PATH):
        folders = os.listdir(path)

        all_face_encodings = {}
        exception_no_face_counter = 0
        exception_memory_counter = 0

        # Load a sample picture and learn how to recognize it.
        for directory in folders:
            path_to_folder_with_images = '{}/{}'.format(path, directory)
            images_in_folder = os.listdir(path_to_folder_with_images)
            for img_index, image in enumerate(images_in_folder):
                directory_name_with_img_index = '{}_img{}'.format(directory.capitalize(), img_index)
                path_to_singe_image = '{}/{}'.format(path_to_folder_with_images, image)
                print(path_to_folder_with_images, image)
                image = face_recognition.load_image_file(path_to_singe_image)
                try:
                    all_face_encodings[directory_name_with_img_index] = \
                    FaceDataHelper.custom_face_encodings_with_large_model_for_landmarks(image,
                                                                                        FaceDataHelper.get_face_locations_with_all_models(
                                                                                            image))[0]
                except MemoryError:
                    print('EXCEPTION MemoryError! ', path_to_singe_image)
                    exception_memory_counter += 1
                except IndexError:
                    # If photo doesn't have faces or models can't detect face
                    print('EXCEPTION IndexError! ', path_to_singe_image)
                    exception_no_face_counter += 1

            print('folder: ', path_to_folder_with_images, 'count of photos without faces: ', exception_no_face_counter)
            print('folder: ', path_to_folder_with_images, 'memory exceptions: ', exception_memory_counter)
            exception_no_face_counter = 0

        return all_face_encodings

    @staticmethod
    def get_face_encodings_from_local_video(path=PERSONS_VIDEO_PATH):
        video_dict = DataWorker.get_dict_of_video_and_user_id_in_folder(path)
        return DataWorker.get_face_encodings_from_video_dict(video_dict)

    @staticmethod
    def get_face_encodings_from_video_dict(video_dict, path_to_dataset_for_updating=None, face_encodings_data=None):
        """
        Given an dictionary, with path to training video and user id, return the encoded faces for each frame of video

        :param video_dict: Dictionary, with path to training video and user id
        :param path_to_dataset_for_updating: Path to dataset from which we will take index for updating data
        :param face_encodings_data: face encodings data
        :return: The encoded faces for each frame of video
        """

        # 1. Create temp variable for result and counting frames in video
        all_face_encodings = {}
        frame_counter = 0

        # 2. Parse dictionary with video and user_id
        for video_file, user_id in video_dict.items():
            print("processing video:", video_file)

            # 3. Read video
            video_capture = cv2.VideoCapture(video_file)

            # 4. Get count of encoded face in dataset for specific user
            last_position_in_dataset = 0

            if path_to_dataset_for_updating or face_encodings_data:
                last_position_in_dataset = DataWorker.get_last_position_in_dataset(path_to_dataset_for_updating,
                                                                                   'video', user_id,
                                                                                   face_encodings_data)
            # FIXME: There is no certainty that the correct orientation will return
            # 5. Process a video for getting angle for rotating video if it needed
            rotation_degree = FrameProcessor.get_rotation_degree_for_video(video_file)

            # FIXME: It should process video one time
            # 6. Process the video the second time for getting face encodings
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break

                # 7. Rotate video to the correct orientation
                frame = FrameProcessor.rotate_image(frame, rotation_degree)

                # 8. Try to get face locations on frame
                face_locations = FaceDataHelper.get_face_locations_with_all_models(frame)

                if face_locations:
                    # 9. Put user id and encoded face location to dictionary
                    user_id_with_frame_index = '{}_frame{}'.format(user_id,
                                                                   frame_counter + last_position_in_dataset + 1)
                    print(user_id_with_frame_index)
                    all_face_encodings[user_id_with_frame_index] = \
                    FaceDataHelper.custom_face_encodings_with_large_model_for_landmarks(frame, face_locations,
                                                                                        num_jitters=1)[0]
                    frame_counter += 1

            # Release software resource and release hardware resource
            video_capture.release()
        return all_face_encodings

    @staticmethod
    def get_face_encodings_from_image_dict(image_dict, path_to_dataset_for_updating=None, face_encodings_data=None):
        """
        Given an dictionary, with path to training image and user id, return the dict with
        index started from last index in`dataset_for_updating` and encoded faces for each image.


        :param image_dict:  Dictionary , with path to training image and user id
        :param path_to_dataset_for_updating: Path to dataset from which we will take index for updating data
        :param face_encodings_data: face encodings data
        :return: The encoded faces for each image
        """

        all_face_encodings = {}
        exception_no_face_counter = 0
        exception_memory_counter = 0

        last_position_in_dataset = 0

        for index, (path_to_singe_image, user_id) in enumerate(image_dict.items()):
            print("processing image:", path_to_singe_image)
            image = face_recognition.load_image_file(path_to_singe_image)

            if path_to_dataset_for_updating or face_encodings_data:
                last_position_in_dataset = DataWorker.get_last_position_in_dataset(path_to_dataset_for_updating,
                                                                                   'image', user_id,
                                                                                   face_encodings_data)

            user_id_with_img_index = '{}_img{}'.format(user_id, index + last_position_in_dataset + 1)
            print(user_id_with_img_index)
            try:
                all_face_encodings[user_id_with_img_index] = \
                    FaceDataHelper.custom_face_encodings_with_large_model_for_landmarks(image,
                                                                                        FaceDataHelper.get_face_locations_with_all_models(
                                                                                            image))[0]
            except MemoryError:
                print('EXCEPTION MemoryError! ', path_to_singe_image)
                exception_memory_counter += 1
            except IndexError:
                # If photo doesn't have faces or models can't detect face
                print('EXCEPTION IndexError! ', path_to_singe_image)
                exception_no_face_counter += 1
        return all_face_encodings

    @staticmethod
    def get_dict_of_video_and_user_id_in_folder(path=PERSONS_VIDEO_PATH):
        video_to_user = {}
        folders = os.listdir(path)
        for user_id in folders:
            path_to_user_video = '{}/{}'.format(path, user_id)
            if not os.path.isdir(path_to_user_video):
                continue
            video_in_folder = os.listdir(path_to_user_video)
            for file in video_in_folder:
                path_to_video = '{}/{}/{}'.format(path, user_id, file)
                video_to_user[path_to_video] = user_id
        return video_to_user

    @staticmethod
    def _save_face_encodings(all_face_encodings, full_path):
        with open(full_path, 'wb') as f:
            pickle.dump(all_face_encodings, f)

    @staticmethod
    def get_last_position_in_dataset(dataset_path, data_type, user_id, face_encodings_data):
        """
        Function for get last index of encoded face from photo or video frame

        :param dataset_path: path to dataset file with face encodings, using if face_encodings is None
        :param data_type: Type of encoded data with person face
        :param user_id: Id of person
        :param face_encodings_data: face encodings data
        :return:
        """
        if face_encodings_data:
            all_face_encodings = face_encodings_data
        else:
            all_face_encodings = DataWorker.load_face_encodings(dataset_path)

        if data_type == 'image':
            delimiter = '{}_img'.format(user_id)
        elif data_type == 'video':
            delimiter = '{}_frame'.format(user_id)
        else:
            return 0

        all_keys_by_user_id = [int(key.split(delimiter)[1]) for key, value in all_face_encodings.items() if
                               delimiter in key.lower()]

        if all_keys_by_user_id:
            return max(all_keys_by_user_id)
        else:
            return 0
