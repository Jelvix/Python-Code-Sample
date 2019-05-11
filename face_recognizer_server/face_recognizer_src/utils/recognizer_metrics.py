import face_recognition
import cv2
from imutils.video import FileVideoStream
from face_recognizer_src.settings import BASE_PATH, CAFFE_PROTO_TXT_PATH, CAFFE_MODEL_PATH

video = BASE_PATH+'/test_video/face_look_at_phone0.avi'


class FaceRecognizerCNN:
    @staticmethod
    def print_metrics(path_to_video):
        video_capture = cv2.VideoCapture(path_to_video)
        count_of_detected_faces = 0
        # Count of frames in video which get manually
        count_of_frames = 466
        current_frame = 1
        while video_capture.isOpened():
            print('FaceRecognizerCNN Process {} / {} frames'. format(current_frame, count_of_frames))
            ret, frame = video_capture.read()
            try:
                face_locations = face_recognition.face_locations(frame, model='cnn')
            except TypeError:
                break
            count_of_detected_faces += len(face_locations)
            current_frame += 1
        video_capture.release()
        result = "FaceRecognizerCNN - Count of detected faces: ", count_of_detected_faces
        return result


class FaceRecognizerHog:
    @staticmethod
    def print_metrics(path_to_video):
        video_capture = cv2.VideoCapture(path_to_video)
        count_of_detected_faces = 0
        # Count of frames in video which get manually
        count_of_frames = 466
        current_frame = 1
        while video_capture.isOpened():
            print('FaceRecognizerHog Process {} / {} frames'.format(current_frame, count_of_frames))
            ret, frame = video_capture.read()
            try:
                face_locations = face_recognition.face_locations(frame)
            except TypeError:
                break
            count_of_detected_faces += len(face_locations)
            current_frame += 1
        video_capture.release()
        result = "FaceRecognizerHog - Count of detected faces: ", count_of_detected_faces
        return result


class FaceRecognizerCaffe:
    @staticmethod
    def print_metrics(path_to_video):
        args = {"prototxt": CAFFE_PROTO_TXT_PATH, "model": CAFFE_MODEL_PATH, "confidence": 0.5}
        net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
        fvs = FileVideoStream(path_to_video).start()
        # Count of frames in video which get manually
        count_of_frames = 466
        current_frame = 1
        count_of_detected_faces = 0
        while fvs.more():
            print('FaceRecognizerCaffe Process {} / {} frames'.format(current_frame, count_of_frames))

            # grab the frame from the threaded video stream
            frame = fvs.read()

            try:
                # grab the frame dimensions and convert it to a blob
                (h, w) = frame.shape[:2]
            except AttributeError:
                break
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

            # pass the blob through the network and obtain the detections and
            # predictions
            net.setInput(blob)
            detections = net.forward()
            # loop over the detections
            count_of_face_in_frame = 0
            for i in range(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with the
                # prediction
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by ensuring the `confidence` is
                # greater than the minimum confidence
                if confidence < args["confidence"]:
                    continue
                count_of_face_in_frame += 1

            count_of_detected_faces += count_of_face_in_frame
            current_frame += 1
        fvs.stop()
        result = "FaceRecognizerCaffe - Count of detected faces: ", count_of_detected_faces
        return result


hog = FaceRecognizerHog()
cnn = FaceRecognizerCNN()
caffe = FaceRecognizerCaffe()

models = [hog, cnn, caffe]
results = []

for model in models:
    results.append(model.print_metrics(video))

for res in results:
    print(res)
