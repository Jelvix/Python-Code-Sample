#!/bin/bash

celery -A face_recognizer_server.celery_config worker -E -n worker.recognizer -Q recognizer --loglevel=DEBUG &
celery -A face_recognizer_server.celery_config worker -E -n worker.dashboard_statistics -Q dashboard_statistics --loglevel=DEBUG
