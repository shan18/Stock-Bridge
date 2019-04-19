from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic import RedirectView

from .views import HomeView
from accounts.views import RegisterView, LoginView, logout_view


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^market/', include('market.urls', namespace='market')),
    url(r'^account/', include('accounts.urls', namespace='account')),
    url(r'^accounts/', include('accounts.passwords.urls')),
    url(r'^accounts/$', RedirectView.as_view(url='/account')),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
