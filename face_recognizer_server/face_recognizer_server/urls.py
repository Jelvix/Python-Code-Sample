from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from stuff.views import GetPersonsByCompanyId, PostConcretePersonActionHistory
from dashboard.views import DashboardListView, PersonStatisticsViewSet

urlpatterns = [
    path('', DashboardListView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('get_persons_by_company/', GetPersonsByCompanyId.as_view(), name='get-persons-by-company'),
    path('get_stats_by_person/', PersonStatisticsViewSet.as_view({'get': 'get_stats_by_person_id'}), name='get-stats-by-person-id'),
    path('get_stats_by_company/', PersonStatisticsViewSet.as_view({'get': 'get_stats_by_company_id'}), name='get-stats-by-company-id'),
    path('recognize_persons_on_image/', PostConcretePersonActionHistory.as_view(), name='recognize-persons-on-image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
