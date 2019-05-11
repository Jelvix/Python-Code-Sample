import dlib
import cv2
import numpy as np

predictor_model = "shape_predictor_68_face_landmarks.dat"
face_pose_predictor = dlib.shape_predictor(predictor_model)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
face_detector = dlib.get_frontal_face_detector()

skip_frame_rate = 3

# resize_rate = 0.25
resize_rate = 1


def main():
    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    i = 0
    while True:
        i += 1
        if i % skip_frame_rate == 0:
            i = 1
        else:
            continue
        # Grab a single frame of video
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=resize_rate, fy=resize_rate)

        faces = face_detector(gray, 1)
        for i, face_rect in enumerate(faces):
            cv2.rectangle(frame, (int(face_rect.left() / resize_rate), int(face_rect.top() / resize_rate)),
                          (int(face_rect.right() / resize_rate), int(face_rect.bottom() / resize_rate)), (255, 0, 0), 2)
            # Get the the face's pose
            pose_landmarks = face_pose_predictor(gray, face_rect)
            draw_face(frame, pose_landmarks)
            # print dir(pose_landmarks)
        # faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        # for (x, y, w, h) in faces:
        #     cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow("Video", frame)
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def draw_polyline(img, detections, start, end, is_closed=0):
    print(dir(detections))
    print(dir(detections.parts()[0]))
    print(dir(detections.rect))
    # print dir(detections.parts)
    # print dir(detections.parts)
    print(detections.parts()[0])
    points = np.array([[int(point.x/resize_rate), int(point.y/resize_rate)] for point in detections.parts()[start:end]])
    cv2.polylines(img, np.int32([points]), is_closed, (0, 255, 0), 2)


def draw_face(img, detections):
    if detections.num_parts != 68:
        return
    draw_polyline(img, detections, 0, 16)  # Jaw line
    draw_polyline(img, detections, 17, 21)  # Left eyebrow
    draw_polyline(img, detections, 22, 26)  # Right eyebrow
    draw_polyline(img, detections, 27, 30)  # Nose bridge
    draw_polyline(img, detections, 30, 35, 1)  # Lower nose
    draw_polyline(img, detections, 36, 41, 1)  # Left eye
    draw_polyline(img, detections, 42, 47, 1)  # Right Eye
    draw_polyline(img, detections, 48, 59, 1)  # Outer lip
    draw_polyline(img, detections, 60, 67, 1)  # Inner lip


if __name__ == '__main__':
    main()
