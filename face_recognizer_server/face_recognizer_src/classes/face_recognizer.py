import face_recognition

from itertools import compress
from face_recognizer_src.classes.face_data_helper import FaceDataHelper


class FaceRecognizer:
    def __init__(self, faces_dataset, tolerance=0.31):
        self.faces_dataset = faces_dataset
        self.tolerance = tolerance

    def get_face_names_and_locations(self, frame, confidence=0.7):
        # Caffe face detection model
        face_locations = FaceDataHelper.get_face_locations_by_caffe_model(frame, confidence)

        face_names_in_frame = []
        faces_from_dataset = []
        faces_list_names_from_dataset = []

        for item in self.faces_dataset:
            faces_from_dataset.append(self.faces_dataset[item])
            faces_list_names_from_dataset.append(item)

        for face_encoding in FaceDataHelper.custom_face_encodings_with_large_model_for_landmarks(frame, face_locations):
            name = self.get_name_of_person_by_image(face_encoding,
                                                    faces_from_dataset,
                                                    faces_list_names_from_dataset)
            face_names_in_frame.append(name)
        print("Stuff ids: ", face_names_in_frame)
        return face_names_in_frame, face_locations

    def get_name_of_person_by_image(self, frame, encoded_face_list, faces_list_names):
        # See if the face is a match for the known face(s)
        match = face_recognition.compare_faces(encoded_face_list, frame, self.tolerance)
        # Get indexes of recognized faces
        recognized_idx = list(compress(range(len(match)), match))
        return FaceRecognizer.get_name_of_recognized_person(faces_list_names, recognized_idx)

    @staticmethod
    def get_name_of_recognized_person(faces_list, recognized_idx):
        name = "Unknown"
        if len(faces_list) > 0:
            for i in recognized_idx:
                name = "_".join(faces_list[i].split("_")[:-1])
            return name
        else:
            return name
