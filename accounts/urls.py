from django.conf.urls import url

from .views import (
    AccountEmailActivateView, LoanView, cancel_loan, close_bank, deduct_interest, ScheduleView, ScheduleDeleteView
)


app_name = 'Account'


urlpatterns = [
    url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', AccountEmailActivateView.as_view(), name='email-activate'),
    url(r'^email/resend-activation/$', AccountEmailActivateView.as_view(), name='resend-activation'),
    url(r'^bank/loan$', LoanView.as_view(), name='loan'),
    url(r'^bank/loan/deduct$', cancel_loan, name='cancel_loan'),
    url(r'^bank/close$', close_bank, name='close_bank'),
    url(r'^bank/interest/deduct$', deduct_interest, name='deduct_interest'),
    url(r'^schedules/(?P<username>[a-zA-Z0-9]+)/$', ScheduleView.as_view(), name='schedules'),
    url(r'^schedules/(?P<username>[a-zA-Z0-9]+)/delete/(?P<pk>\d+)$', ScheduleDeleteView.as_view(), name='delete_schedule'),
]
