import cv2
from face_recognizer_src.classes.frame_adapter import FrameAdapter
from face_recognizer_src.classes.face_data_helper import FaceDataHelper


class FrameProcessor:
    def __init__(self, frame_adapter=FrameAdapter(0.5)):
        self.resize_coef = frame_adapter.resize_coef

    def draw_rectangles_on_frame(self, frame, face_locations, face_names, frame_name):
        """
        Function for drawing the name of person below the detected face

        :param frame: Frame of image as numpy array
        :param face_locations: Position of detected face on frame
        :param face_names: Name of detected person on frame
        :param frame_name: Name of window for showing video
        :return: Display the resulting frame
        """
        font = cv2.FONT_HERSHEY_DUPLEX

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= int(1 / self.resize_coef)
            right *= int(1 / self.resize_coef)
            bottom *= int(1 / self.resize_coef)
            left *= int(1 / self.resize_coef)

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting frame
        cv2.imshow(frame_name, frame)

    @staticmethod
    def get_image_in_four_rotation(image_as_numpy):
        """
        1. Grab the dimensions of the image and calculate the center of the image
        2. Create list of images in four rotations

        :param image_as_numpy: Image for rotation
        :return: List of images in four rotations
        """
        (h, w) = image_as_numpy.shape[:2]
        center = (w / 2, h / 2)
        degree = 90

        four_rotation_of_frame = [
            cv2.warpAffine(image_as_numpy, cv2.getRotationMatrix2D(center, degree * i, 1.0), (w, h)) for i in range(0, 4)]
        return four_rotation_of_frame

    @staticmethod
    def get_rotation_degree_for_video(path_to_video_file, video_validation_face_limit=40):
        """
        1. Create dict with different rotations
        2. Read frames from video while video not ended or when we get limit of face detections for some orientation
        3. Return value of degree for rotation

        :param path_to_video_file: Path to video file for checking orientation
        :param video_validation_face_limit: max count of face detections for  orientation
        :return: Value of degree for rotation
        """
        print("Check orientation of video {}".format(path_to_video_file))
        degree = 90
        rotation = {0: 0, 90: 0, 180: 0, 270: 0}

        video_capture = cv2.VideoCapture(path_to_video_file)
        while max(rotation.values()) < video_validation_face_limit:
            ret, frame = video_capture.read()
            if not ret:
                break
            rotated_frames = FrameProcessor.get_image_in_four_rotation(frame)
            for index, rotated_frame in enumerate(rotated_frames):
                face_locations = FaceDataHelper.get_face_locations_with_all_models(rotated_frame)
                if face_locations:
                    rotation[index * degree] += 1

        # Release handle to the webcam
        video_capture.release()
        return max(rotation)

    @staticmethod
    def rotate_image(image_as_numpy, rotation_degree):
        """
        1. Checking is image need rotation, if not, just return base image
        2. If image need rotation, grab the dimensions of the image and calculate the center of the image
        3. Apply rotation by center to image

        :param image_as_numpy: Base image
        :param rotation_degree: Angle of needed rotation
        :return: Rotated image as numpy
        """
        if rotation_degree == 0:
            return image_as_numpy
        (h, w) = image_as_numpy.shape[:2]
        center = (w / 2, h / 2)
        return cv2.warpAffine(image_as_numpy, cv2.getRotationMatrix2D(center, rotation_degree, 1.0), (w, h))
