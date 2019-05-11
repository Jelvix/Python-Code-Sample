import cv2
import os

from pathlib import Path
from face_recognizer_src.settings import BASE_PATH
from face_recognizer_src.classes.face_recognizer import FaceRecognizer
from face_recognizer_src.classes.frame_adapter import FrameAdapter
from face_recognizer_src.classes.frame_processor import FrameProcessor
from face_recognizer_src.classes.data_worker import DataWorker


def run(faces_dataset, camera_id, tolerance=0.31, confidence=0.9):
    """
    This is a running face recognition on live video from your webcam.
    Given a face dataset, camera id, return the live video output with recognitions

    1. Process each video frame in full resolution
    2. Only detect faces in every other frame of video.

    :param faces_dataset:
    :param camera_id:
    :param tolerance:
    :param confidence:
    :return:
    """
    resize_coef = 1

    face_recognizer = FaceRecognizer(faces_dataset, tolerance)
    frame_adapter = FrameAdapter(resize_coef)
    frame_processor = FrameProcessor(frame_adapter)

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(camera_id)

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        if ret is False:
            break

        small_frame = frame_adapter.process_frame(frame)

        # Find all the faces and face encodings in the current frame of video
        face_names, face_locations = face_recognizer.get_face_names_and_locations(small_frame, confidence=confidence)

        # continue
        frame_processor.draw_rectangles_on_frame(frame, face_locations, face_names, str(camera_id))

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


def main(camera_id=0):
    dataset_path = os.path.join(BASE_PATH, 'datasets/dataset_faces.dat')
    # Save or load trained model if exists
    if Path(dataset_path).is_file():
        run(DataWorker.load_face_encodings(dataset_path), camera_id, tolerance=0.31, confidence=0.9)
    else:
        face_encodings = DataWorker.get_face_encodings_from_local_images()
        face_encodings.update(DataWorker.get_face_encodings_from_local_video())
        run(DataWorker.create_faces_dataset(face_encodings, dataset_path), camera_id, tolerance=0.31, confidence=0.9)


if __name__ == '__main__':
    main()
