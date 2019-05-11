from face_recognizer_server.celery_config import app


@app.task(queue="dashboard_statistics")
def create_person_statistic_obj_for_yesterday_task():
    from .views import create_person_statistic_obj_for_yesterday
    from datetime import datetime
    from company.models import Company

    companies = Company.objects.all()
    for company in companies:
        if datetime.now(company.timezone).strftime('%H') == '00':
            create_person_statistic_obj_for_yesterday(company)
        else:
            continue
