import cv2
import face_recognition
import os
from face_recognizer_src.settings import BASE_PATH
from multiprocessing import Process
import requests
import time


def main(camera_id, door_id):
    video_capture = cv2.VideoCapture(camera_id)
    # i = 0
    while True:
        # # Get every 5'th frame of video
        # i += 1
        # if i % 5 == 0:
        #     i = 1
        # else:
        #     continue

        name = "person.jpg"

        # Grab a single frame of video
        for i in range(4):
            video_capture.grab()
        ret, frame = video_capture.read()

        face_locations = face_recognition.face_locations(frame)

        if len(face_locations) > 0:
            cv2.imwrite(name, frame)

            with open(name, 'rb') as file:
                files = {
                    'file': file,
                    'Content-Type': 'image/jpeg'
                }
                r = requests.post(
                    'http://0.0.0.0:8000/api/recognizer/persons/',
                    verify=False, files=files, data={"door": door_id}
                )
                print('camera_id :', camera_id, 'response: ', r.text)

            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # time.sleep(3)

        cv2.imshow(str(camera_id), frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main(BASE_PATH + '/test_video/face_look_at_phone0.avi', 1)
    # cam1 = Process(target=main, args=(1, 1))
    # cam2 = Process(target=main, args=(0, 2))
    #
    # cam1.start()
    # cam2.start()
