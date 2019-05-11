CELERY_CONFIG=face_recognizer_server.celery_config

celery_beat:
	rm -f celerybeat-schedule && rm -f celerybeat-schedule.db && rm -f celerybeat.pid  && celery -A $(CELERY_CONFIG) beat --loglevel=DEBUG

install_requirements:
	pip3 install -r /app/requirements.txt

# celery scripts
celery:
	chmod +x ./bash_scripts/start_periodical_tasks.sh && ./bash_scripts/start_periodical_tasks.sh