import numpy as np
import face_recognition
import cv2

from face_recognition.api import _raw_face_landmarks, face_encoder
from face_recognizer_src.settings import CAFFE_PROTO_TXT_PATH, CAFFE_MODEL_PATH


class FaceDataHelper:
    def __init__(self):
        pass

    @staticmethod
    def custom_face_encodings_with_large_model_for_landmarks(face_image, known_face_locations=None, num_jitters=1):
        """
        Given an image, return the 128-dimension face encoding for each face in the image.

        :param face_image: The image that contains one or more faces
        :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
        :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
        :return: A list of 128-dimensional face encodings (one for each face in the image)
        """
        raw_landmarks = _raw_face_landmarks(face_image, known_face_locations, model="large")
        return [np.array(face_encoder.compute_face_descriptor(face_image, raw_landmark_set, num_jitters)) for
                raw_landmark_set in raw_landmarks]

    @staticmethod
    def get_face_locations_with_all_models(image):
        """
        Given an image, return the tuple of rect points (top, right, bottom, left) for each face in the image.
        Apply hog, cnn, caffe face detection models to an image.

        :param image: The image that contains one or more faces
        :return: A list of tuples of rect points (top, right, bottom, left) for each face in the image.
        """

        models_functions = [
            FaceDataHelper.get_face_locations_by_caffe_model,
            face_recognition.face_locations,
            FaceDataHelper.get_face_locations_by_default_cnn
        ]
        for detection_func in models_functions:
            encodings = detection_func(image)
            if len(encodings) > 0:
                return encodings
        return []

    @staticmethod
    def get_face_locations_by_caffe_model(image, confidence_arg=0.9):
        """
        Given an image, return the tuple of rect points (top, right, bottom, left) for each face in the image.
        Apply caffe face detection model to an image.

        :param image: The image that contains one or more faces
        :param confidence_arg: minimum probability of finding a person's face
        :return: A list of tuples of rect points (top, right, bottom, left) for each face in the image.
        """

        net = cv2.dnn.readNetFromCaffe(CAFFE_PROTO_TXT_PATH, CAFFE_MODEL_PATH)
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        face_locations = []
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence < confidence_arg:
                continue
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (left, top, right, bottom) = box.astype("int")

            face_location_tuple = (top, right, bottom, left)
            face_locations.append(face_location_tuple)

        return face_locations

    @staticmethod
    def get_face_locations_by_default_cnn(image):
        """
        Given an image, return the tuple of rect points (top, right, bottom, left) for each face in the image.
        Apply cnn face detection model to an image.

        :param image: The image that contains one or more faces
        :return: A list of tuples of rect points (top, right, bottom, left) for each face in the image.
        """

        return face_recognition.face_locations(image, number_of_times_to_upsample=1, model='cnn')