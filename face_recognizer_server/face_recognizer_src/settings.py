import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PERSONS_VIDEO_PATH = os.path.join(BASE_PATH, 'persons_video')
PERSONS_PHOTO_PATH = os.path.join(BASE_PATH, 'persons_photos')
CAFFE_PROTO_TXT_PATH = os.path.join(BASE_PATH, 'models/deploy.prototxt.txt')
CAFFE_MODEL_PATH = os.path.join(BASE_PATH, 'models/res10_300x300_ssd_iter_140000.caffemodel')
