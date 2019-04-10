from django.conf.urls import url
from .views import CompanySelectionView
app_name = 'Market'


urlpatterns = [
    url(r'^select/$', CompanySelectionView.as_view(), name='company_select'),
    ]





