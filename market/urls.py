from django.conf.urls import url
from .views import CompanyTransactionView
app_name = 'Market'


urlpatterns = [
    url(r'^transact/(?P<code>\w+)$', CompanyTransactionView.as_view(), name='transaction'),
    ]





