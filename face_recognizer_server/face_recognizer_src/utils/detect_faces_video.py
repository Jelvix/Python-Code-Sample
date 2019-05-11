# import the necessary packages
from imutils.video import VideoStream, FileVideoStream
import numpy as np
import time
import cv2
from face_recognizer_src.settings import CAFFE_PROTO_TXT_PATH, CAFFE_MODEL_PATH

args = {"prototxt": CAFFE_PROTO_TXT_PATH, "model": CAFFE_MODEL_PATH, "confidence": 0.5}


# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
# vs = FileVideoStream(BASE_PATH+'/test_video/face_look_at_phone0.avi').start()
time.sleep(2.0)
count_of_detected_faces = 0

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream
	frame = vs.read()
	try:
		# grab the frame dimensions and convert it to a blob
		(h, w) = frame.shape[:2]
	except AttributeError:
		print("FaceRecognizerCaffe - Count of detected faces: ", count_of_detected_faces)
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

		# compute the (x, y)-coordinates of the bounding box for the
		# object
		box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
		(startX, startY, endX, endY) = box.astype("int")

		# draw the bounding box of the face along with the associated
		# probability
		text = "{:.2f}%".format(confidence * 100)
		y = startY - 10 if startY - 10 > 10 else startY + 10
		crop_frame = frame[startY:endY, startX:endX]
		cv2.imwrite('1.jpg', crop_frame)
		count_of_face_in_frame += 1
		cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 2)
		cv2.putText(frame, text, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

	# show the output frame
	print('count_of_face_in_frame: ', count_of_face_in_frame)
	count_of_detected_faces += count_of_face_in_frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		print("FaceRecognizerCaffe - Count of detected faces: ", count_of_detected_faces)
		break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
